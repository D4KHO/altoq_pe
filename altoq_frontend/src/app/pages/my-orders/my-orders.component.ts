import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { OrderService } from '../../services/order';
import { ChatService } from '../../services/chat.service';
import { ToastService } from '../../services/toast.service';
import { MapboxService } from '../../services/mapbox.service';
import { DeliveryService } from '../../services/delivery.service';
import { User } from '../../models/auth';
import { Order } from '../../models/order';

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './my-orders.component.html',
  styleUrls: ['./my-orders.component.css']
})
export class MyOrdersComponent implements OnInit, OnDestroy {
  user: User | null = null;
  orders: Order[] = [];

  ordersLoading = false;
  ordersError = '';

  // Order filtering and pagination
  ordersFilter: 'all' | 'pending' | 'completed' | 'canceled' = 'all';
  ordersPage = 1;
  ordersPageSize = 5;

  // Support Chat logic
  openChatOrderId: number | null = null;
  chatMessages: any[] = [];
  chatId: number | null = null;
  newChatMessage: string = '';
  chatLoading = false;
  chatError = '';

  // Expandable Detail & Map Tracking
  expandedOrderId: number | null = null;
  mapInstance: any = null;
  clientMarker: any = null;
  sellerMarker: any = null;
  trackingInterval: any = null;

  constructor(
    private authService: AuthService,
    private orderService: OrderService,
    private chatService: ChatService,
    private toastService: ToastService,
    private mapboxService: MapboxService,
    private deliveryService: DeliveryService
  ) {}

  ngOnInit(): void {
    this.authService.user$.subscribe(user => {
      if (user) {
        this.user = user;
      }
    });
    this.loadOrders();
  }

  ngOnDestroy(): void {
    this.cleanupMap();
  }

  loadOrders(): void {
    this.ordersLoading = true;
    this.ordersError = '';
    this.orderService.getUserOrders().subscribe({
      next: (orders) => {
        this.orders = orders;
        this.ordersLoading = false;
      },
      error: (err) => {
        console.error('Error loading orders:', err);
        this.ordersError = 'No se pudieron cargar tus pedidos. Intenta de nuevo.';
        this.ordersLoading = false;
      }
    });
  }

  // ===== FILTERING & PAGINATION =====

  getFilteredOrders(): Order[] {
    if (this.ordersFilter === 'all') {
      return this.orders;
    } else if (this.ordersFilter === 'pending') {
      return this.orders.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'delivering');
    } else if (this.ordersFilter === 'completed') {
      return this.orders.filter(o => o.status === 'completed');
    } else if (this.ordersFilter === 'canceled') {
      return this.orders.filter(o => o.status === 'canceled');
    }
    return this.orders;
  }

  getPaginatedOrders(): Order[] {
    const filtered = this.getFilteredOrders();
    const startIndex = (this.ordersPage - 1) * this.ordersPageSize;
    return filtered.slice(startIndex, startIndex + this.ordersPageSize);
  }

  getOrdersTotalPages(): number {
    const count = this.getFilteredOrders().length;
    return Math.ceil(count / this.ordersPageSize) || 1;
  }

  setOrdersFilter(filter: 'all' | 'pending' | 'completed' | 'canceled'): void {
    this.ordersFilter = filter;
    this.ordersPage = 1;
    this.openChatOrderId = null; // Close open chats when switching tabs
    this.expandedOrderId = null;
    this.cleanupMap();
  }

  nextOrdersPage(): void {
    if (this.ordersPage < this.getOrdersTotalPages()) {
      this.ordersPage++;
      this.expandedOrderId = null;
      this.cleanupMap();
    }
  }

  prevOrdersPage(): void {
    if (this.ordersPage > 1) {
      this.ordersPage--;
      this.expandedOrderId = null;
      this.cleanupMap();
    }
  }

  getOrderCountByStatus(status: 'pending' | 'completed' | 'canceled'): number {
    if (status === 'pending') {
      return this.orders.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'delivering').length;
    }
    return this.orders.filter(o => o.status === status).length;
  }

  // ===== DETAIL EXPANSION & MAPS =====

  toggleOrderDetail(order: Order): void {
    this.cleanupMap();

    if (this.expandedOrderId === order.id) {
      this.expandedOrderId = null;
    } else {
      this.expandedOrderId = order.id || null;
      if (order.status === 'delivering' && order.delivery_token) {
        setTimeout(() => {
          this.initMapForOrder(order);
        }, 100);
      }
    }
  }

  initMapForOrder(order: Order): void {
    const clientLat = order.shipping_latitude || -5.1945;
    const clientLng = order.shipping_longitude || -80.6300;

    const mapboxgl = (window as any).mapboxgl;
    if (!mapboxgl) {
      console.error('Mapbox GL JS library not loaded');
      return;
    }

    mapboxgl.accessToken = this.mapboxService.getToken();

    const mapContainerId = `map-${order.id}`;
    const mapEl = document.getElementById(mapContainerId);
    if (!mapEl) {
      console.error('Map container element not found:', mapContainerId);
      return;
    }

    this.mapInstance = new mapboxgl.Map({
      container: mapContainerId,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [Number(clientLng), Number(clientLat)],
      zoom: 14
    });

    // Marcador Cliente (Destino)
    this.clientMarker = new mapboxgl.Marker({ color: '#ef4444' })
      .setLngLat([Number(clientLng), Number(clientLat)])
      .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(
        `<div style="padding: 2px;"><p style="margin:0; font-weight:bold; font-size:12px; color:#1e293b;">Tu ubicación de entrega</p></div>`
      ))
      .addTo(this.mapInstance);

    this.clientMarker.togglePopup();

    // Actualización inicial
    this.updateMapPositionsForOrder(order);

    // Polling cada 5 segundos
    this.trackingInterval = setInterval(() => {
      this.updateMapPositionsForOrder(order);
    }, 5000);
  }

  updateMapPositionsForOrder(order: Order): void {
    if (!order.delivery_token) return;

    this.deliveryService.trackDelivery(order.delivery_token).subscribe({
      next: (data: any) => {
        // Si el estado en base de datos cambia, actualizar orden local
        if (order.status !== data.delivery_status) {
          order.status = data.delivery_status;
          order.delivery_status = data.delivery_status;
          if (data.delivery_status === 'completed' || data.delivery_status === 'canceled') {
            this.cleanupMap();
            return;
          }
        }

        const sellerLat = data.delivery_latitude;
        const sellerLng = data.delivery_longitude;

        if (sellerLat === null || sellerLng === null || !this.mapInstance) return;

        const sellerPos: [number, number] = [Number(sellerLng), Number(sellerLat)];
        const mapboxgl = (window as any).mapboxgl;

        if (!this.sellerMarker) {
          this.sellerMarker = new mapboxgl.Marker({ color: '#4f46e5' })
            .setLngLat(sellerPos)
            .addTo(this.mapInstance);
        } else {
          this.sellerMarker.setLngLat(sellerPos);
        }

        const origin = sellerPos;
        const destination: [number, number] = [
          Number(data.shipping_longitude),
          Number(data.shipping_latitude)
        ];

        this.mapboxService.getRoute(origin, destination).subscribe({
          next: (res: any) => {
            if (res && res.routes && res.routes.length > 0 && this.mapInstance) {
              const routeGeometry = res.routes[0].geometry;

              if (this.mapInstance.getSource('route')) {
                this.mapInstance.getSource('route').setData({
                  type: 'Feature',
                  properties: {},
                  geometry: routeGeometry
                });
              } else {
                this.mapInstance.addSource('route', {
                  type: 'geojson',
                  data: {
                    type: 'Feature',
                    properties: {},
                    geometry: routeGeometry
                  }
                });

                this.mapInstance.addLayer({
                  id: 'route',
                  type: 'line',
                  source: 'route',
                  layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                  },
                  paint: {
                    'line-color': '#4f46e5',
                    'line-width': 5,
                    'line-opacity': 0.85
                  }
                });
              }

              const bounds = new mapboxgl.LngLatBounds()
                .extend(origin)
                .extend(destination);
              
              this.mapInstance.fitBounds(bounds, { padding: 40 });
            }
          },
          error: (err: any) => console.error('Error loading inline Mapbox route:', err)
        });
      },
      error: (err: any) => {
        console.error('Error polling inline tracking coordinates:', err);
      }
    });
  }

  cleanupMap(): void {
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }
    this.sellerMarker = null;
    this.clientMarker = null;
    if (this.mapInstance) {
      try {
        this.mapInstance.remove();
      } catch (e) {
        console.warn('Error removing Mapbox GL instance:', e);
      }
      this.mapInstance = null;
    }
  }

  // ===== UTILS =====

  getStatusLabel(status: string): string {
    const map: Record<string, string> = {
      'pending': 'Creado',
      'confirmed': 'Aceptado',
      'delivering': 'En camino',
      'completed': 'Entregado',
      'canceled': 'Cancelado'
    };
    return map[status] || status;
  }

  getStatusClass(status: string): string {
    const map: Record<string, string> = {
      'pending': 'bg-slate-100 text-slate-700 border border-slate-200',
      'confirmed': 'bg-blue-50 text-blue-700 border border-blue-100',
      'delivering': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
      'completed': 'bg-green-50 text-green-700 border border-green-100',
      'canceled': 'bg-red-50 text-red-700 border border-red-100'
    };
    return map[status] || 'bg-slate-100 text-slate-700';
  }

  getProductCount(order: Order): number {
    return (order.products || []).reduce((sum, p: any) => sum + (p.quantity || 1), 0);
  }

  copyCode(code: string): void {
    navigator.clipboard.writeText(code);
    this.toastService.show('Código copiado al portapapeles', 'success');
  }

  formatTime(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(dateStr: string | Date | undefined): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  // ===== SUPPORT CHAT =====

  openOrderChat(order: Order): void {
    if (this.openChatOrderId === order.id) {
      this.openChatOrderId = null;
      return;
    }

    const products: any[] = order.products || [];
    if (!products.length) return;

    const firstProduct = products[0];
    const productId = firstProduct.productId;

    this.openChatOrderId = order.id!;
    this.chatLoading = true;
    this.chatError = '';
    this.chatMessages = [];
    this.chatId = null;

    this.chatService.startChatForOrder(order.id!, productId).subscribe({
      next: (chat: any) => {
        this.chatId = chat.id;
        this.loadChatMessages(chat.id);
      },
      error: (err: any) => {
        console.error('Error starting order chat:', err);
        this.chatError = 'No se pudo iniciar el chat. El vendedor debe tener una tienda activa.';
        this.chatLoading = false;
      }
    });
  }

  loadChatMessages(chatId: number): void {
    this.chatService.getChatMessages(chatId).subscribe({
      next: (messages) => {
        this.chatMessages = messages;
        this.chatLoading = false;
        setTimeout(() => {
          const chatEl = document.getElementById('orderChatMessages');
          if (chatEl) {
            chatEl.scrollTop = chatEl.scrollHeight;
          }
        }, 100);
      },
      error: (err) => {
        console.error('Error loading chat messages:', err);
        this.chatLoading = false;
      }
    });
  }

  sendChatMessage(): void {
    if (!this.newChatMessage.trim() || !this.chatId) return;

    const content = this.newChatMessage;
    this.newChatMessage = '';

    this.chatService.sendMessage(this.chatId, content).subscribe({
      next: (msg) => {
        this.chatMessages.push(msg);
        setTimeout(() => {
          const chatEl = document.getElementById('orderChatMessages');
          if (chatEl) {
            chatEl.scrollTop = chatEl.scrollHeight;
          }
        }, 50);
      },
      error: (err) => {
        console.error('Error sending chat message:', err);
        this.newChatMessage = content;
      }
    });
  }

  isMyMessage(message: any): boolean {
    return Number(message.sender_id) === Number(this.user?.id);
  }
}


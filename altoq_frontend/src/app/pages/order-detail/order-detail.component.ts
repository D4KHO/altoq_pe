import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { OrderService } from '../../services/order';
import { ChatService } from '../../services/chat.service';
import { ToastService } from '../../services/toast.service';
import { MapboxService } from '../../services/mapbox.service';
import { DeliveryService } from '../../services/delivery.service';
import { User } from '../../models/auth';
import { Order } from '../../models/order';
import { ReviewService } from '../../services/review.service';

@Component({
  selector: 'app-order-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './order-detail.component.html',
  styleUrls: ['./order-detail.component.css']
})
export class OrderDetailComponent implements OnInit, OnDestroy {
  user: User | null = null;
  orderId!: number;
  order: Order | null = null;
  loading = true;
  error = '';

  // Support Chat logic
  chatMessages: any[] = [];
  chatId: number | null = null;
  newChatMessage: string = '';
  chatLoading = false;
  chatError = '';

  // Map Tracking
  mapInstance: any = null;
  clientMarker: any = null;
  sellerMarker: any = null;
  trackingInterval: any = null;

  // Reviews logic
  orderReviews: any[] = [];
  showReviewModal = false;
  selectedProductToReview: any = null;
  reviewRating = 5;
  reviewStoreRating = 5;
  reviewComment = '';
  reviewImageFile: File | null = null;
  reviewImagePreview: string | null = null;
  isSubmittingReview = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private orderService: OrderService,
    private chatService: ChatService,
    private toastService: ToastService,
    private mapboxService: MapboxService,
    private deliveryService: DeliveryService,
    private reviewService: ReviewService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.error = 'ID de pedido no válido';
      this.loading = false;
      return;
    }
    this.orderId = Number(idParam);

    this.authService.user$.subscribe(user => {
      if (user) {
        this.user = user;
      }
    });

    this.loadOrderDetails();
  }

  ngOnDestroy(): void {
    this.cleanupMap();
  }

  loadOrderDetails(): void {
    this.loading = true;
    this.error = '';
    this.orderService.getOrderById(this.orderId).subscribe({
      next: (order) => {
        this.order = order;
        this.loading = false;
        
        // Start map tracking if in delivering status
        if (order.status === 'delivering' && order.delivery_token) {
          setTimeout(() => {
            this.initMapForOrder(order);
          }, 100);
        }

        // Open chat initially if the order is not canceled
        if (order.status !== 'canceled') {
          this.initOrderChat(order);
        }

        // Load reviews if the order is completed
        if (order.status === 'completed') {
          this.loadOrderReviews();
        }
      },
      error: (err) => {
        console.error('Error loading order details:', err);
        this.error = 'No se pudo cargar la información del pedido. Intenta de nuevo.';
        this.loading = false;
      }
    });
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

    const mapContainerId = 'order-detail-map';
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

    // Marcador Cliente (Destino) - Custom SVG House
    const elClient = document.createElement('div');
    elClient.className = 'custom-client-marker';
    elClient.style.display = 'flex';
    elClient.style.alignItems = 'center';
    elClient.style.justifyContent = 'center';
    elClient.style.width = '42px';
    elClient.style.height = '42px';
    elClient.style.backgroundColor = '#ef4444';
    elClient.style.border = '3px solid #ffffff';
    elClient.style.borderRadius = '50%';
    elClient.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)';
    elClient.style.color = 'white';
    elClient.style.cursor = 'pointer';
    elClient.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="width: 22px; height: 22px;">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    `;

    this.clientMarker = new mapboxgl.Marker(elClient)
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
          // Marcador Repartidor (Moto) - Custom SVG
          const elSeller = document.createElement('div');
          elSeller.className = 'custom-seller-marker';
          elSeller.style.display = 'flex';
          elSeller.style.alignItems = 'center';
          elSeller.style.justifyContent = 'center';
          elSeller.style.width = '42px';
          elSeller.style.height = '42px';
          elSeller.style.backgroundColor = '#4f46e5';
          elSeller.style.border = '3px solid #ffffff';
          elSeller.style.borderRadius = '50%';
          elSeller.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)';
          elSeller.style.color = 'white';
          elSeller.style.cursor = 'pointer';
          elSeller.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 24px; height: 24px;">
              <!-- Rueda trasera -->
              <circle cx="6" cy="17" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
              <!-- Rueda delantera -->
              <circle cx="18" cy="17" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
              <!-- Caja de delivery -->
              <rect x="3" y="8" width="5" height="5" rx="1" fill="currentColor"/>
              <!-- Chasis/Cuerpo scooter -->
              <path d="M6 17h12M8.5 13H14l2.5 4M13 13l1.5-4h2.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <!-- Manubrio -->
              <path d="M17 9l-1.5-3h-2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          `;

          this.sellerMarker = new mapboxgl.Marker(elSeller)
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
          error: (err: any) => console.error('Error loading route:', err)
        });
      },
      error: (err: any) => {
        console.error('Error polling tracking coordinates:', err);
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

  initOrderChat(order: Order): void {
    const products: any[] = order.products || [];
    if (!products.length) return;

    const firstProduct = products[0];
    const productId = firstProduct.productId;

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
        this.chatError = 'No se pudo iniciar el chat de soporte con el vendedor.';
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
          const chatEl = document.getElementById('orderDetailChatMessages');
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
          const chatEl = document.getElementById('orderDetailChatMessages');
          if (chatEl) {
            chatEl.scrollTop = chatEl.scrollHeight;
          }
        }, 50);
      },
      error: (err) => {
        console.error('Error sending chat message:', err);
        this.newChatMessage = content;
        
        // Mostrar mensaje de error del backend (como la alerta de seguridad)
        const errorMsg = err.error?.detail || 'No se pudo enviar el mensaje.';
        this.toastService.show(errorMsg, 'error');
      }
    });
  }

  isMyMessage(message: any): boolean {
    return Number(message.sender_id) === Number(this.user?.id);
  }

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

  formatTime(dateStr: string | Date | undefined): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(dateStr: string | Date | undefined): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  loadOrderReviews(): void {
    this.reviewService.getOrderReviews(this.orderId).subscribe({
      next: (reviews) => {
        this.orderReviews = reviews;
      },
      error: (err) => {
        console.error('Error loading order reviews:', err);
      }
    });
  }

  hasBeenReviewed(productId: number): boolean {
    return this.orderReviews.some(r => Number(r.product_id) === Number(productId));
  }

  getReviewForProduct(productId: number): any {
    return this.orderReviews.find(r => Number(r.product_id) === Number(productId));
  }

  openReviewModal(product: any): void {
    this.selectedProductToReview = product;
    this.reviewRating = 5;
    this.reviewStoreRating = 5;
    this.reviewComment = '';
    this.reviewImageFile = null;
    this.reviewImagePreview = null;
    this.showReviewModal = true;
  }

  closeReviewModal(): void {
    this.showReviewModal = false;
    this.selectedProductToReview = null;
  }

  setReviewRating(rating: number): void {
    this.reviewRating = rating;
  }

  setReviewStoreRating(rating: number): void {
    this.reviewStoreRating = rating;
  }

  onReviewImageSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        this.toastService.show('Por favor selecciona una imagen válida', 'error');
        return;
      }
      this.reviewImageFile = file;
      const reader = new FileReader();
      reader.onload = () => {
        this.reviewImagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  submitReview(): void {
    if (!this.selectedProductToReview) return;
    this.isSubmittingReview = true;

    const saveReview = (imageUrl?: string) => {
      const reviewData = {
        product_id: this.selectedProductToReview.productId,
        order_id: this.orderId,
        rating: this.reviewRating,
        store_rating: this.reviewStoreRating,
        comment: this.reviewComment || undefined,
        image_url: imageUrl || undefined
      };

      this.reviewService.createReview(reviewData).subscribe({
        next: (review) => {
          this.toastService.show('¡Reseña publicada exitosamente!', 'success');
          this.orderReviews.push(review);
          this.loadOrderReviews();
          this.isSubmittingReview = false;
          this.closeReviewModal();
        },
        error: (err) => {
          console.error('Error submitting review:', err);
          this.toastService.show('Error al publicar la reseña: ' + (err.error?.detail || err.message), 'error');
          this.isSubmittingReview = false;
        }
      });
    };

    if (this.reviewImageFile) {
      this.reviewService.uploadReviewImage(this.reviewImageFile).subscribe({
        next: (res) => {
          saveReview(res.image_url);
        },
        error: (err) => {
          console.error('Error uploading review image:', err);
          this.toastService.show('Error al subir la imagen, guardando reseña sin foto...', 'info');
          saveReview();
        }
      });
    } else {
      saveReview();
    }
  }
}

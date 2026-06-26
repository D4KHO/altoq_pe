import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { OrderService } from '../../services/order';
import { DeliveryService } from '../../services/delivery.service';
import { MapboxService } from '../../services/mapbox.service';
import { ToastService } from '../../services/toast.service';
import { Order } from '../../models/order';

@Component({
  selector: 'app-delivery-manage',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './delivery-manage.component.html',
  styleUrl: './delivery-manage.component.css'
})
export class DeliveryManageComponent implements OnInit, OnDestroy {
  orderId!: number;
  order: Order | null = null;
  loading = true;

  // Seguimiento GPS
  watchId: number | null = null;
  currentLat: number | null = null;
  currentLng: number | null = null;

  // Mapbox
  map: any = null;
  sellerMarker: any = null;
  clientMarker: any = null;

  // Formulario de Validación
  validationCode = '';
  validating = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private orderService: OrderService,
    private deliveryService: DeliveryService,
    private mapboxService: MapboxService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.toastService.show('ID de pedido no proporcionado', 'error');
      this.router.navigate(['/seller-area']);
      return;
    }

    this.orderId = Number(idParam);
    this.loadOrderDetails();
  }

  ngOnDestroy(): void {
    this.stopTracking();
  }

  loadOrderDetails(): void {
    this.loading = true;
    this.orderService.getOrderById(this.orderId).subscribe({
      next: (order) => {
        this.order = order;
        this.loading = false;

        // Si ya está en curso la entrega, reanudar geolocalización automáticamente
        if (order.status === 'delivering') {
          this.startTracking();
        }

        // Cargar mapa
        this.loadMap();
      },
      error: (err) => {
        console.error(err);
        this.toastService.show('Error al cargar detalles del pedido', 'error');
        this.loading = false;
        this.router.navigate(['/seller-area']);
      }
    });
  }

  loadMap(): void {
    setTimeout(() => {
      this.initMap();
    }, 100);
  }

  initMap(): void {
    if (!this.order) return;

    // Destino (Comprador)
    const clientLat = this.order.shipping_latitude || -5.1945;
    const clientLng = this.order.shipping_longitude || -80.6300;

    const mapboxgl = (window as any).mapboxgl;
    if (!mapboxgl) {
      console.error('Mapbox GL JS library not loaded');
      return;
    }

    mapboxgl.accessToken = this.mapboxService.getToken();

    this.map = new mapboxgl.Map({
      container: 'manageMap',
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
        `<div style="padding: 2px;"><p style="margin:0; font-weight:bold; font-size:12px; color:#1e293b;">Entregar aquí</p><p style="margin:2px 0 0 0; font-size:10px; color:#64748b;">${this.order.shipping_address}</p></div>`
      ))
      .addTo(this.map);

    this.clientMarker.togglePopup();

    this.updateRouteOnMap();
  }

  startDelivery(): void {
    this.loading = true;
    // Intentar obtener ubicación inicial antes de llamar a la API
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.callStartApi(coords);
        },
        (error) => {
          console.warn('Geolocation error before start, starting without initial coords:', error);
          this.callStartApi({});
        }
      );
    } else {
      this.callStartApi({});
    }
  }

  callStartApi(coords: { latitude?: number; longitude?: number }): void {
    this.deliveryService.startDelivery(this.orderId, coords).subscribe({
      next: (res: any) => {
        this.toastService.show('¡Ruta de entrega iniciada! Geolocalización activa.', 'success');
        if (this.order) {
          this.order.status = 'delivering';
          this.order.delivery_status = 'delivering';
          this.order.delivery_token = res.delivery_token;
        }
        this.startTracking();
        this.updateRouteOnMap();
        this.loading = false;
      },
      error: (err: any) => {
        console.error(err);
        this.toastService.show('Error al iniciar la entrega', 'error');
        this.loading = false;
      }
    });
  }

  startTracking(): void {
    if (this.watchId) return;

    if (navigator.geolocation) {
      this.watchId = navigator.geolocation.watchPosition(
        (position) => {
          this.currentLat = position.coords.latitude;
          this.currentLng = position.coords.longitude;

          // Actualizar marcador
          this.updateSellerMarker();
          this.updateRouteOnMap();

          // Enviar coordenadas al backend
          this.deliveryService.updateLocation(this.orderId, {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }).subscribe({
            error: (err: any) => console.error('Error updating location on backend:', err)
          });
        },
        (error) => {
          console.error('Error watching location:', error);
          this.toastService.show('Error al obtener tu ubicación GPS. Asegúrate de tener activada la ubicación.', 'info');
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      this.toastService.show('Tu navegador no soporta geolocalización', 'error');
    }
  }

  stopTracking(): void {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }

  updateSellerMarker(): void {
    if (!this.map || this.currentLat === null || this.currentLng === null) return;

    const sellerPos: [number, number] = [this.currentLng, this.currentLat];
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
        <svg xmlns="http://www.w3.org/2050/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 24px; height: 24px;">
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
        .addTo(this.map);
    } else {
      this.sellerMarker.setLngLat(sellerPos);
    }
  }

  updateRouteOnMap(): void {
    if (!this.map || this.currentLat === null || this.currentLng === null || !this.order) return;

    const origin: [number, number] = [this.currentLng, this.currentLat];
    const destination: [number, number] = [Number(this.order.shipping_longitude), Number(this.order.shipping_latitude)];

    this.mapboxService.getRoute(origin, destination).subscribe({
      next: (res: any) => {
        if (res && res.routes && res.routes.length > 0) {
          const routeGeometry = res.routes[0].geometry;
          const mapboxgl = (window as any).mapboxgl;

          if (this.map.getSource('route')) {
            this.map.getSource('route').setData({
              type: 'Feature',
              properties: {},
              geometry: routeGeometry
            });
          } else {
            this.map.addSource('route', {
              type: 'geojson',
              data: {
                type: 'Feature',
                properties: {},
                geometry: routeGeometry
              }
            });

            this.map.addLayer({
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
          
          this.map.fitBounds(bounds, { padding: 50 });
        }
      },
      error: (err: any) => {
        console.error('Error fetching route:', err);
      }
    });
  }

  validateCode(): void {
    if (!this.validationCode || this.validationCode.length < 4) {
      this.toastService.show('Por favor ingresa un código de entrega válido', 'info');
      return;
    }

    this.validating = true;
    this.deliveryService.validateDeliveryCode(this.validationCode.trim().toUpperCase()).subscribe({
      next: (res: any) => {
        this.toastService.show('¡Código validado! Entrega completada y pago liberado.', 'success');
        this.stopTracking();
        if (this.order) {
          this.order.status = 'completed';
          this.order.delivery_status = 'completed';
        }
        this.validating = false;
      },
      error: (err: any) => {
        console.error(err);
        this.toastService.show(err.error?.detail || 'Error al validar el código', 'error');
        this.validating = false;
      }
    });
  }

  get trackingUrl(): string {
    if (!this.order || !this.order.delivery_token) return '';
    const base = window.location.origin;
    return `${base}/delivery/track/${this.order.delivery_token}`;
  }

  copyTrackingLink(): void {
    const url = this.trackingUrl;
    if (url) {
      navigator.clipboard.writeText(url).then(() => {
        this.toastService.show('Enlace copiado al portapapeles', 'success');
      });
    }
  }

  shareOnWhatsApp(): void {
    const url = this.trackingUrl;
    if (!url || !this.order) return;
    const clientName = this.order.client_name || 'Cliente';
    const message = `¡Hola ${clientName}! Estoy en camino a tu domicilio para entregar tu pedido. Puedes seguir mi ubicación en tiempo real aquí: ${url}`;
    const encodedText = encodeURIComponent(message);
    const whatsappUrl = `https://api.whatsapp.com/send?phone=${this.order.contact_phone}&text=${encodedText}`;
    window.open(whatsappUrl, '_blank');
  }
}

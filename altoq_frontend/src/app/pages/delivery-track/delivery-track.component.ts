import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { DeliveryService } from '../../services/delivery.service';
import { MapboxService } from '../../services/mapbox.service';

@Component({
  selector: 'app-delivery-track',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './delivery-track.component.html',
  styleUrl: './delivery-track.component.css'
})
export class DeliveryTrackComponent implements OnInit, OnDestroy {
  token!: string;
  deliveryData: any = null;
  loading = true;
  error = '';

  // Polling
  pollInterval: any = null;

  // Mapbox
  map: any = null;
  sellerMarker: any = null;
  clientMarker: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private deliveryService: DeliveryService,
    private mapboxService: MapboxService
  ) {}

  ngOnInit(): void {
    const tokenParam = this.route.snapshot.paramMap.get('token');
    if (!tokenParam) {
      this.error = 'Token de seguimiento no válido o no proporcionado.';
      this.loading = false;
      return;
    }

    this.token = tokenParam;
    this.loadTrackingData(true); // Carga inicial que monta el mapa
    
    // Iniciar sondeo (polling) cada 5 segundos
    this.pollInterval = setInterval(() => {
      this.loadTrackingData(false);
    }, 5000);
  }

  ngOnDestroy(): void {
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }

  loadTrackingData(isInitial: boolean): void {
    this.deliveryService.trackDelivery(this.token).subscribe({
      next: (data: any) => {
        this.deliveryData = data;
        this.loading = false;

        if (isInitial) {
          this.loadMap();
        } else {
          this.updateMapPositions();
        }

        // Si la entrega ya terminó, detener el polling
        if (data.delivery_status === 'completed' || data.delivery_status === 'canceled') {
          if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
          }
        }
      },
      error: (err: any) => {
        console.error(err);
        this.error = 'No se pudo cargar la información de seguimiento. El enlace puede haber expirado o ser inválido.';
        this.loading = false;
        if (this.pollInterval) {
          clearInterval(this.pollInterval);
          this.pollInterval = null;
        }
      }
    });
  }

  loadMap(): void {
    setTimeout(() => {
      this.initMap();
    }, 100);
  }

  initMap(): void {
    if (!this.deliveryData) return;

    const clientLat = this.deliveryData.shipping_latitude || -5.1945;
    const clientLng = this.deliveryData.shipping_longitude || -80.6300;

    const mapboxgl = (window as any).mapboxgl;
    if (!mapboxgl) {
      console.error('Mapbox GL JS library not loaded');
      return;
    }

    mapboxgl.accessToken = this.mapboxService.getToken();

    this.map = new mapboxgl.Map({
      container: 'trackMap',
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
      .addTo(this.map);

    this.clientMarker.togglePopup();

    this.updateMapPositions();
  }

  updateMapPositions(): void {
    if (!this.map || !this.deliveryData) return;

    const sellerLat = this.deliveryData.delivery_latitude;
    const sellerLng = this.deliveryData.delivery_longitude;

    if (sellerLat === null || sellerLng === null) return;

    const sellerPos: [number, number] = [Number(sellerLng), Number(sellerLat)];
    const mapboxgl = (window as any).mapboxgl;

    if (!this.sellerMarker) {
      this.sellerMarker = new mapboxgl.Marker({ color: '#4f46e5' })
        .setLngLat(sellerPos)
        .addTo(this.map);
    } else {
      this.sellerMarker.setLngLat(sellerPos);
    }

    // Dibujar ruta
    const origin = sellerPos;
    const destination: [number, number] = [
      Number(this.deliveryData.shipping_longitude),
      Number(this.deliveryData.shipping_latitude)
    ];

    this.mapboxService.getRoute(origin, destination).subscribe({
      next: (res: any) => {
        if (res && res.routes && res.routes.length > 0) {
          const routeGeometry = res.routes[0].geometry;

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
        console.error('Error updating tracking route:', err);
      }
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}

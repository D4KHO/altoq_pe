import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class GoogleMapsLoaderService {
  private loaded = false;
  private loadPromise: Promise<void> | null = null;

  load(): Promise<void> {
    if (this.loaded) return Promise.resolve();
    if (this.loadPromise) return this.loadPromise;

    this.loadPromise = new Promise((resolve, reject) => {
      // Si ya está cargado globalmente en window
      if (typeof window !== 'undefined' && (window as any).google && (window as any).google.maps) {
        this.loaded = true;
        resolve();
        return;
      }

      const script = document.createElement('script');
      // Cargamos el SDK de Google Maps con la biblioteca places (para geocodificación y autocompletado si fuese necesario)
      script.src = `https://maps.googleapis.com/maps/api/js?libraries=places`;
      script.async = true;
      script.defer = true;
      script.onload = () => {
        this.loaded = true;
        resolve();
      };
      script.onerror = (err) => {
        reject(err);
      };
      document.head.appendChild(script);
    });

    return this.loadPromise;
  }
}

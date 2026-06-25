import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MapboxService {
  private token = environment.mapboxToken;

  constructor(private http: HttpClient) {}

  getToken(): string {
    return this.token;
  }

  getRoute(origin: [number, number], destination: [number, number]): Observable<any> {
    // origin y destination en formato [lng, lat]
    const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${origin[0]},${origin[1]};${destination[0]},${destination[1]}?geometries=geojson&access_token=${this.token}`;
    return this.http.get<any>(url);
  }

  reverseGeocode(lng: number, lat: number): Observable<any> {
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?access_token=${this.token}&types=address`;
    return this.http.get<any>(url);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DeliveryService {
  private apiUrl = `${environment.apiUrl}/delivery`;

  constructor(private http: HttpClient) {}

  generateDeliveryCode(orderId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/generate/${orderId}`, {});
  }

  validateDeliveryCode(code: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/validate`, { code });
  }

  getDeliveryCodeByOrder(orderId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/order/${orderId}`);
  }

  startDelivery(orderId: number, coords: { latitude?: number; longitude?: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/start/${orderId}`, coords);
  }

  updateLocation(orderId: number, coords: { latitude: number; longitude: number }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/update-location/${orderId}`, coords);
  }

  trackDelivery(token: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/track/${token}`);
  }
}

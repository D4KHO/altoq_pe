import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DeliveryService {
  private apiUrl = 'http://localhost:8000/api/delivery';

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
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Order } from '../models/order';
import { AuthService } from './auth.service';


@Injectable({
  providedIn: 'root',
})
export class OrderService {
  private apiUrl = 'http://localhost:8000/api/orders';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ){}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  createOrder(order: Omit<Order, 'id' | 'created_at' | 'updated_at'>): Observable<Order> {
    return this.http.post<Order>(this.apiUrl, order, { headers: this.getHeaders() });
  }

  getUserOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(`${this.apiUrl}/user`, { headers: this.getHeaders() });
  } 

  getOrderById(id:number): Observable<Order> {
    return this.http.get<Order>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }

  updateOrderStatus(id: number , status: string): Observable<Order> {
    return this.http.put<Order>(`${this.apiUrl}/${id}/status`, { status }, { headers: this.getHeaders() });
  }

  cancelOrder(id:number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }


}
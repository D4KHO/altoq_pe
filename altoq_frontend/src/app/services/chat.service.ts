import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = `${environment.apiUrl}/chat`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({ 'Authorization': `Bearer ${token}` });
  }

  startChat(sellerId: number, productId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/start`, { seller_id: sellerId, product_id: productId }, { headers: this.getHeaders() });
  }

  /** Inicia (o recupera) un chat de soporte vinculado a un pedido específico. El seller_id lo resuelve el backend. */
  startChatForOrder(orderId: number, productId: number): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/start-for-order`,
      { order_id: orderId, product_id: productId },
      { headers: this.getHeaders() }
    );
  }

  getMyChats(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my-chats`, { headers: this.getHeaders() });
  }

  getChat(chatId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${chatId}`, { headers: this.getHeaders() });
  }

  getChatMessages(chatId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${chatId}/messages`, { headers: this.getHeaders() });
  }

  sendMessage(chatId: number, content: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${chatId}/messages`, { content }, { headers: this.getHeaders() });
  }

  closeChat(chatId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${chatId}/close`, {}, { headers: this.getHeaders() });
  }
}

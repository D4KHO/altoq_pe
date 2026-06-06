import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = 'http://localhost:8000/api/chat';

  constructor(private http: HttpClient) {}

  startChat(sellerId: number, productId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/start`, { seller_id: sellerId, product_id: productId });
  }

  getMyChats(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my-chats`);
  }

  getChat(chatId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${chatId}`);
  }

  getChatMessages(chatId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${chatId}/messages`);
  }

  sendMessage(chatId: number, content: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${chatId}/messages`, { content });
  }

  closeChat(chatId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/${chatId}/close`, {});
  }
}

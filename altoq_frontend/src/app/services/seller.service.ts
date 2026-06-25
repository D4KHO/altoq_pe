import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SellerService {
  private apiUrl = `${environment.apiUrl}/seller`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  private getParams(): HttpParams {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token found in localStorage');
      return new HttpParams();
    }
    console.log('Token being sent as query param:', token);
    return new HttpParams().set('token', token);
  }

  becomeSeller(storeData: any): Observable<any> {
    const headers = this.getHeaders();
    const params = this.getParams();
    
    console.log('Headers being sent:', headers);
    console.log('Params being sent:', params);
    
    return this.http.post(`${this.apiUrl}/become-seller`, storeData, {
      headers: headers,
      params: params
    });
  }

  switchRole(role: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/switch-role`, null, {
      params: this.getParams().set('role', role),
      headers: this.getHeaders()
    });
  }

  getMyStore(): Observable<any> {
    return this.http.get(`${this.apiUrl}/my-store`, {
      params: this.getParams(),
      headers: this.getHeaders()
    });
  }

  updateStore(storeData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/my-store`, storeData, { params: this.getParams() });
  }

  chatWithAiProductAssistant(messages: any[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/ai-product-assistant/chat`, { messages }, { params: this.getParams() });
  }

  chatWithAiStoreAssistant(messages: { sender: string; content: string }[]): Observable<any> {
    const headers = this.getHeaders();
    const params = this.getParams();

    return this.http.post(`${this.apiUrl}/ai-store-assistant/chat`, { messages }, {
      headers: headers,
      params: params
    });
  }

  getSellerOrders(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/orders`, {
      params: this.getParams(),
      headers: this.getHeaders()
    });
  }

  cancelSellerOrder(orderId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/orders/${orderId}/cancel`, null, {
      params: this.getParams(),
      headers: this.getHeaders()
    });
  }

  updateAutoConfirm(autoConfirm: boolean): Observable<any> {
    return this.http.put(`${this.apiUrl}/my-store/auto-confirm`, null, {
      params: this.getParams().set('auto_confirm', autoConfirm),
      headers: this.getHeaders()
    });
  }

  confirmSellerOrder(orderId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/orders/${orderId}/confirm`, null, {
      params: this.getParams(),
      headers: this.getHeaders()
    });
  }
}

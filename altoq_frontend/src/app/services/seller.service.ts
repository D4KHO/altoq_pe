import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class SellerService {
  private apiUrl = 'http://localhost:8000/api/seller';

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
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { User } from '../models/auth';
import { Address, AddressCreate, AddressUpdate, UserUpdate, PasswordChange } from '../models/user-profile';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  // ===== PROFILE =====

  getProfile(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`, {
      headers: this.getHeaders()
    });
  }

  updateProfile(data: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/me`, data, {
      headers: this.getHeaders()
    });
  }

  changePassword(data: PasswordChange): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(`${this.apiUrl}/me/password`, data, {
      headers: this.getHeaders()
    });
  }

  // ===== ADDRESSES =====

  getAddresses(): Observable<Address[]> {
    return this.http.get<Address[]>(`${this.apiUrl}/me/addresses`, {
      headers: this.getHeaders()
    });
  }

  createAddress(data: AddressCreate): Observable<Address> {
    return this.http.post<Address>(`${this.apiUrl}/me/addresses`, data, {
      headers: this.getHeaders()
    });
  }

  updateAddress(id: number, data: AddressUpdate): Observable<Address> {
    return this.http.put<Address>(`${this.apiUrl}/me/addresses/${id}`, data, {
      headers: this.getHeaders()
    });
  }

  deleteAddress(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.apiUrl}/me/addresses/${id}`, {
      headers: this.getHeaders()
    });
  }
}

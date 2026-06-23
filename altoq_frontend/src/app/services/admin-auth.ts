import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment';

interface AdminLoginRequest {
  username: string;
  password: string;
}

interface AdminResponse {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  created_at: string;
  last_login: string | null;
}

interface AdminTokenResponse {
  access_token: string;
  token_type: string;
  admin: AdminResponse;
}

@Injectable({
  providedIn: 'root'
})
export class AdminAuthService {
  private apiUrl = `${environment.apiUrl}/admin`;
  private tokenKey = 'admin_token';
  private adminSubject = new BehaviorSubject<AdminResponse | null>(this.getAdminFromStorage());
  
  public admin$ = this.adminSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  private getAdminFromStorage(): AdminResponse | null {
    const adminData = localStorage.getItem('admin_data');
    return adminData ? JSON.parse(adminData) : null;
  }

  login(credentials: AdminLoginRequest): Observable<AdminTokenResponse> {
    return this.http.post<AdminTokenResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap(response => {
        localStorage.setItem(this.tokenKey, response.access_token);
        localStorage.setItem('admin_data', JSON.stringify(response.admin));
        this.adminSubject.next(response.admin);
      })
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem('admin_data');
    this.adminSubject.next(null);
    this.router.navigate(['/admin/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentAdmin(): Observable<AdminResponse> {
    return this.http.get<AdminResponse>(`${this.apiUrl}/me`);
  }
}

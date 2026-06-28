import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AdminAuthService } from './admin-auth';
import { environment } from '../../environments/environment';

export interface AdminMetricsSummary {
  total_revenue: number;
  total_orders: number;
  total_users: number;
  total_buyers: number;
  total_sellers: number;
  total_stores: number;
  active_stores: number;
  pending_stores: number;
  suspended_stores: number;
  total_visits: number;
  total_chats: number;
  total_templates: number;
}

export interface AdminMetricChartPoint {
  date: string;
  revenue: number;
  orders: number;
  chats: number;
  new_users: number;
}

export interface AdminStoreRanking {
  store_id: number;
  name: string;
  owner_name: string | null;
  email: string;
  revenue: number;
  orders_count: number;
  avg_rating: number;
  visits_count: number;
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class AdminMetricsService {
  private apiUrl = `${environment.apiUrl}/admin/metrics`;

  constructor(private http: HttpClient, private authService: AdminAuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getSummary(): Observable<AdminMetricsSummary> {
    const headers = this.getHeaders();
    return this.http.get<AdminMetricsSummary>(`${this.apiUrl}/summary`, { headers });
  }

  getCharts(days: number = 30): Observable<AdminMetricChartPoint[]> {
    const headers = this.getHeaders();
    return this.http.get<AdminMetricChartPoint[]>(`${this.apiUrl}/charts?days=${days}`, { headers });
  }

  getRankings(limit: number = 5): Observable<AdminStoreRanking[]> {
    const headers = this.getHeaders();
    return this.http.get<AdminStoreRanking[]>(`${this.apiUrl}/rankings?limit=${limit}`, { headers });
  }
}

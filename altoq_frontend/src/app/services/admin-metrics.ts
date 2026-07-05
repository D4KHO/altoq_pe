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

  getSummary(startDate?: string, endDate?: string): Observable<AdminMetricsSummary> {
    const headers = this.getHeaders();
    let url = `${this.apiUrl}/summary`;
    if (startDate && endDate) {
      url += `?start_date=${startDate}&end_date=${endDate}`;
    }
    return this.http.get<AdminMetricsSummary>(url, { headers });
  }

  getCharts(days: number = 30, startDate?: string, endDate?: string): Observable<AdminMetricChartPoint[]> {
    const headers = this.getHeaders();
    let url = `${this.apiUrl}/charts?days=${days}`;
    if (startDate && endDate) {
      url = `${this.apiUrl}/charts?start_date=${startDate}&end_date=${endDate}`;
    }
    return this.http.get<AdminMetricChartPoint[]>(url, { headers });
  }

  getRankings(limit: number = 5): Observable<AdminStoreRanking[]> {
    const headers = this.getHeaders();
    return this.http.get<AdminStoreRanking[]>(`${this.apiUrl}/rankings?limit=${limit}`, { headers });
  }

  exportMetrics(startDate?: string, endDate?: string): Observable<Blob> {
    const headers = this.getHeaders();
    let url = `${this.apiUrl}/export`;
    if (startDate && endDate) {
      url += `?start_date=${startDate}&end_date=${endDate}`;
    }
    return this.http.get(url, {
      headers,
      responseType: 'blob'
    });
  }
}

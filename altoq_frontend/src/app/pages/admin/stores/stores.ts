import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AdminAuthService } from '../../../services/admin-auth';
import { environment } from '../../../../environments/environment';

interface Store {
  id: number;
  name: string;
  email: string;
  owner_name: string | null;
  phone: string | null;
  description: string | null;
  logo: string | null;
  created_at: string;
  status: string;
}

@Component({
  selector: 'app-stores',
  imports: [CommonModule],
  templateUrl: './stores.html',
  styleUrl: './stores.css'
})
export class Stores implements OnInit {
  stores: Store[] = [];
  isLoading = false;

  constructor(private http: HttpClient, private authService: AdminAuthService) {}

  ngOnInit(): void {
    this.loadStores();
  }

  loadStores(): void {
    this.isLoading = true;
    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<Store[]>(`${environment.apiUrl}/admin/stores/`, { headers }).subscribe({
      next: (stores) => {
        this.stores = stores;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading stores:', error);
        this.isLoading = false;
      }
    });
  }

  getStatusText(status: string): string {
    const statusMap: { [key: string]: string } = {
      'active': 'Activa',
      'pending': 'Pendiente',
      'suspended': 'Suspendida'
    };
    return statusMap[status] || status;
  }

  changeStatus(store: Store, event: Event): void {
    const newStatus = (event.target as HTMLSelectElement).value;
    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.patch<Store>(
      `${environment.apiUrl}/admin/stores/${store.id}/status`,
      { status: newStatus },
      { headers }
    ).subscribe({
      next: (updatedStore) => {
        store.status = updatedStore.status;
      },
      error: (error) => {
        console.error('Error updating store status:', error);
        alert('Error al actualizar el estado');
      }
    });
  }

  deleteStore(storeId: number): void {
    if (!confirm('¿Estás seguro de que quieres eliminar esta tienda?')) {
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`${environment.apiUrl}/admin/stores/${storeId}`, { headers }).subscribe({
      next: () => {
        this.stores = this.stores.filter(s => s.id !== storeId);
      },
      error: (error) => {
        console.error('Error deleting store:', error);
        alert('Error al eliminar tienda');
      }
    });
  }
}

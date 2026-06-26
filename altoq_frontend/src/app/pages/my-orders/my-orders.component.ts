import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { OrderService } from '../../services/order';
import { ToastService } from '../../services/toast.service';
import { User } from '../../models/auth';
import { Order } from '../../models/order';

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './my-orders.component.html',
  styleUrls: ['./my-orders.component.css']
})
export class MyOrdersComponent implements OnInit {
  user: User | null = null;
  orders: Order[] = [];

  ordersLoading = false;
  ordersError = '';

  // Order filtering and pagination
  ordersFilter: 'all' | 'pending' | 'completed' | 'canceled' = 'all';
  ordersPage = 1;
  ordersPageSize = 5;
  expandedOrderId: number | null = null;

  constructor(
    private authService: AuthService,
    private orderService: OrderService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.authService.user$.subscribe(user => {
      if (user) {
        this.user = user;
      }
    });
    this.loadOrders();
  }

  loadOrders(): void {
    this.ordersLoading = true;
    this.ordersError = '';
    this.orderService.getUserOrders().subscribe({
      next: (orders) => {
        this.orders = orders;
        this.ordersLoading = false;
      },
      error: (err) => {
        console.error('Error loading orders:', err);
        this.ordersError = 'No se pudieron cargar tus pedidos. Intenta de nuevo.';
        this.ordersLoading = false;
      }
    });
  }

  // ===== FILTERING & PAGINATION =====

  getFilteredOrders(): Order[] {
    if (this.ordersFilter === 'all') {
      return this.orders;
    } else if (this.ordersFilter === 'pending') {
      return this.orders.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'delivering');
    } else if (this.ordersFilter === 'completed') {
      return this.orders.filter(o => o.status === 'completed');
    } else if (this.ordersFilter === 'canceled') {
      return this.orders.filter(o => o.status === 'canceled');
    }
    return this.orders;
  }

  getPaginatedOrders(): Order[] {
    const filtered = this.getFilteredOrders();
    const startIndex = (this.ordersPage - 1) * this.ordersPageSize;
    return filtered.slice(startIndex, startIndex + this.ordersPageSize);
  }

  getOrdersTotalPages(): number {
    const count = this.getFilteredOrders().length;
    return Math.ceil(count / this.ordersPageSize) || 1;
  }

  setOrdersFilter(filter: 'all' | 'pending' | 'completed' | 'canceled'): void {
    this.ordersFilter = filter;
    this.ordersPage = 1;
    this.expandedOrderId = null;
  }

  nextOrdersPage(): void {
    if (this.ordersPage < this.getOrdersTotalPages()) {
      this.ordersPage++;
      this.expandedOrderId = null;
    }
  }

  prevOrdersPage(): void {
    if (this.ordersPage > 1) {
      this.ordersPage--;
      this.expandedOrderId = null;
    }
  }

  toggleOrderDetail(order: Order): void {
    if (this.expandedOrderId === order.id) {
      this.expandedOrderId = null;
    } else {
      this.expandedOrderId = order.id || null;
    }
  }

  getOrderCountByStatus(status: 'pending' | 'completed' | 'canceled'): number {
    if (status === 'pending') {
      return this.orders.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'delivering').length;
    }
    return this.orders.filter(o => o.status === status).length;
  }

  // ===== UTILS =====

  getStatusLabel(status: string): string {
    const map: Record<string, string> = {
      'pending': 'Creado',
      'confirmed': 'Aceptado',
      'delivering': 'En camino',
      'completed': 'Entregado',
      'canceled': 'Cancelado'
    };
    return map[status] || status;
  }

  getStatusClass(status: string): string {
    const map: Record<string, string> = {
      'pending': 'bg-slate-100 text-slate-700 border border-slate-200',
      'confirmed': 'bg-blue-50 text-blue-700 border border-blue-100',
      'delivering': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
      'completed': 'bg-green-50 text-green-700 border border-green-100',
      'canceled': 'bg-red-50 text-red-700 border border-red-100'
    };
    return map[status] || 'bg-slate-100 text-slate-700';
  }

  getProductCount(order: Order): number {
    return (order.products || []).reduce((sum, p: any) => sum + (p.quantity || 1), 0);
  }

  copyCode(code: string): void {
    navigator.clipboard.writeText(code);
    this.toastService.show('Código copiado al portapapeles', 'success');
  }

  formatTime(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(dateStr: string | Date | undefined): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric' });
  }
}

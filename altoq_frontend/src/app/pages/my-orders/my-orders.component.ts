import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { OrderService } from '../../services/order';
import { ToastService } from '../../services/toast.service';
import { User } from '../../models/auth';
import { Order } from '../../models/order';
import { ReviewService } from '../../services/review.service';

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

  // Reviews integration
  reviewsByOrder: Record<number, any[]> = {};
  showReviewModal = false;
  selectedProductToReview: any = null;
  selectedOrderToReviewId: number | null = null;
  reviewRating = 5;
  reviewStoreRating = 5;
  reviewComment = '';
  reviewImageFile: File | null = null;
  reviewImagePreview: string | null = null;
  isSubmittingReview = false;

  constructor(
    private authService: AuthService,
    private orderService: OrderService,
    private toastService: ToastService,
    private reviewService: ReviewService
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
      if (order.status === 'completed' && order.id && !this.reviewsByOrder[order.id]) {
        this.loadOrderReviews(order.id);
      }
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

  loadOrderReviews(orderId: number): void {
    this.reviewService.getOrderReviews(orderId).subscribe({
      next: (reviews) => {
        this.reviewsByOrder[orderId] = reviews;
      },
      error: (err) => {
        console.error('Error loading order reviews:', err);
      }
    });
  }

  hasBeenReviewed(orderId: number, productId: number): boolean {
    const list = this.reviewsByOrder[orderId] || [];
    return list.some(r => Number(r.product_id) === Number(productId));
  }

  getReviewForProduct(orderId: number, productId: number): any {
    const list = this.reviewsByOrder[orderId] || [];
    return list.find(r => Number(r.product_id) === Number(productId));
  }

  openReviewModal(order: any, item: any): void {
    this.selectedOrderToReviewId = order.id;
    this.selectedProductToReview = item;
    this.reviewRating = 5;
    this.reviewStoreRating = 5;
    this.reviewComment = '';
    this.reviewImageFile = null;
    this.reviewImagePreview = null;
    this.showReviewModal = true;
  }

  closeReviewModal(): void {
    this.showReviewModal = false;
    this.selectedProductToReview = null;
    this.selectedOrderToReviewId = null;
  }

  setReviewRating(rating: number): void {
    this.reviewRating = rating;
  }

  setReviewStoreRating(rating: number): void {
    this.reviewStoreRating = rating;
  }

  onReviewImageSelected(event: any): void {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        this.toastService.show('Por favor selecciona una imagen válida', 'error');
        return;
      }
      this.reviewImageFile = file;
      const reader = new FileReader();
      reader.onload = () => {
        this.reviewImagePreview = reader.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  submitReview(): void {
    if (!this.selectedProductToReview || !this.selectedOrderToReviewId) return;
    this.isSubmittingReview = true;

    const saveReview = (imageUrl?: string) => {
      const reviewData = {
        product_id: this.selectedProductToReview.productId,
        order_id: this.selectedOrderToReviewId!,
        rating: this.reviewRating,
        store_rating: this.reviewStoreRating,
        comment: this.reviewComment || undefined,
        image_url: imageUrl || undefined
      };

      this.reviewService.createReview(reviewData).subscribe({
        next: (review) => {
          this.toastService.show('¡Reseña publicada exitosamente!', 'success');
          
          if (!this.reviewsByOrder[this.selectedOrderToReviewId!]) {
            this.reviewsByOrder[this.selectedOrderToReviewId!] = [];
          }
          this.reviewsByOrder[this.selectedOrderToReviewId!].push(review);
          
          this.isSubmittingReview = false;
          this.closeReviewModal();
        },
        error: (err) => {
          console.error('Error submitting review:', err);
          this.toastService.show('Error al publicar la reseña: ' + (err.error?.detail || err.message), 'error');
          this.isSubmittingReview = false;
        }
      });
    };

    if (this.reviewImageFile) {
      this.reviewService.uploadReviewImage(this.reviewImageFile).subscribe({
        next: (res) => {
          saveReview(res.image_url);
        },
        error: (err) => {
          console.error('Error uploading review image:', err);
          this.toastService.show('Error al subir la imagen, guardando reseña sin foto...', 'info');
          saveReview();
        }
      });
    } else {
      saveReview();
    }
  }
}

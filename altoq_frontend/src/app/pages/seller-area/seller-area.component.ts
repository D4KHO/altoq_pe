import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { SellerService } from '../../services/seller.service';
import { ProductService } from '../../services/product.service';
import { ToastService } from '../../services/toast.service';
import { AuthService } from '../../services/auth.service';
import { ChatService } from '../../services/chat.service';
import { ReviewService } from '../../services/review.service';

import { ConversationalAssistantComponent } from '../../components/conversational-assistant/conversational-assistant.component';
import { ProductCard } from '../../components/product-card/product-card';

@Component({
  selector: 'app-seller-area',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ConversationalAssistantComponent, ProductCard],
  templateUrl: './seller-area.component.html',
  styleUrls: ['./seller-area.component.css']
})
export class SellerAreaComponent implements OnInit {
  store: any = null;
  storeProducts: any[] = [];
  isLoading = false;
  errorMessage = '';
  showAddProductChat: boolean = false;
  storeTheme: string = 'default';
  currentView: 'store' | 'dashboard' = 'dashboard';
  isEditingStore: boolean = false;
  editedStore: any = {};
  isSaving: boolean = false;
  showProductsView: boolean = false;
  showEditProductModal: boolean = false;
  editingProduct: any = {};
  isSavingProduct: boolean = false;

  sellerInquiries: any[] = [];
  openInquiryId: number | null = null;
  openInquiry: any = null;

  // Seller Dashboard additionals
  user: any = null;
  sellerOrders: any[] = [];
  sellerChats: any[] = [];
  sellerReviews: any[] = [];
  ordersLoading = false;
  chatsLoading = false;
  reviewsLoading = false;
  dashboardTab: 'stats' | 'products' | 'orders' | 'chats' | 'reviews' = 'stats';

  // Order filtering and pagination
  ordersFilter: 'all' | 'pending' | 'completed' | 'canceled' = 'all';
  ordersPage = 1;
  ordersPageSize = 5;

  // Reusable confirmation modal state
  showConfirmModal = false;
  confirmModalTitle = '';
  confirmModalMessage = '';
  confirmActionCallback: (() => void) | null = null;

  // Chat support properties
  openChatId: number | null = null;
  chatMessages: any[] = [];
  newChatMessage: string = '';
  chatLoading = false;
  chatError = '';



  constructor(
    private sellerService: SellerService,
    private productService: ProductService,
    private toastService: ToastService,
    private authService: AuthService,
    private chatService: ChatService,
    private reviewService: ReviewService,
    private router: Router
  ) {}

  ngOnInit(): void {
    console.log('SellerAreaComponent initialized');
    this.authService.user$.subscribe(u => {
      this.user = u;
    });
    this.loadMyStore();
  }

  loadMyStore(): void {
    console.log('Loading store...');
    this.isLoading = true;
    this.errorMessage = '';

    this.sellerService.getMyStore().subscribe({
      next: (response) => {
        console.log('Store loaded:', response);
        this.store = response;
        this.determineTheme();
        this.loadStoreProducts();
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading store:', error);
        this.errorMessage = error.error?.detail || 'Error al cargar tu tienda. Por favor, intenta nuevamente.';
        this.isLoading = false;
      }
    });
  }

  determineTheme(): void {
    if (this.store && this.store.theme) {
      this.storeTheme = this.store.theme;
    } else {
      this.storeTheme = 'default';
    }
  }

  loadStoreProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        this.storeProducts = products.filter(p => Number(p.store_id) === Number(this.store?.id));
      },
      error: (error) => {
        console.error('Error loading products:', error);
      }
    });
  }

  toggleAddProductChat(): void {
    this.showAddProductChat = !this.showAddProductChat;
  }

  toggleProductsView(): void {
    this.showProductsView = !this.showProductsView;
  }

  editProduct(product: any): void {
    this.editingProduct = { ...product };
    this.showEditProductModal = true;
  }

  closeEditModal(): void {
    this.showEditProductModal = false;
    this.editingProduct = {};
  }

  saveProductChanges(): void {
    if (!this.editingProduct.name || !this.editingProduct.price) {
      this.toastService.show('Por favor, completa el nombre y precio del producto', 'error');
      return;
    }

    this.isSavingProduct = true;

    this.productService.updateProduct(this.editingProduct.id, this.editingProduct).subscribe({
      next: (response) => {
        this.loadStoreProducts();
        this.closeEditModal();
        this.isSavingProduct = false;
        this.toastService.show('Producto actualizado exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error updating product:', error);
        this.isSavingProduct = false;
        this.toastService.show('Error al actualizar el producto. Por favor, intenta nuevamente.', 'error');
      }
    });
  }

  deleteProduct(productId: number): void {
    this.openConfirmModal(
      'Eliminar Producto',
      '¿Estás seguro de que quieres eliminar este producto? Esta acción no se puede deshacer.',
      () => {
        this.productService.deleteProduct(productId).subscribe({
          next: () => {
            this.loadStoreProducts();
            this.toastService.show('Producto eliminado exitosamente', 'success');
          },
          error: (error) => {
            console.error('Error deleting product:', error);
            this.toastService.show('Error al eliminar el producto. Por favor, intenta nuevamente.', 'error');
          }
        });
      }
    );
  }

  onProductCreated(): void {
    this.loadStoreProducts();
  }

  switchView(view: 'store' | 'dashboard'): void {
    this.currentView = view;
  }

  getThemeGradient(): string {
    const customBgColor = this.isEditingStore ? this.editedStore?.background_color : this.store?.background_color;
    if (customBgColor && customBgColor !== '#f8fafc' && customBgColor !== '') {
      return customBgColor;
    }

    const themeToUse = this.isEditingStore ? this.editedStore?.theme : this.store?.theme;
    const gradients: Record<string, string> = {
      bakery: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
      fashion: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      home: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      food: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      tech: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      default: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    };
    return gradients[themeToUse ?? 'default'] ?? gradients['default'];
  }

  getLayoutClass(): string {
    const layout = this.isEditingStore ? this.editedStore?.layout_type : this.store?.layout_type;
    return `layout-${layout ?? 'grid-3'}`;
  }

  getBackgroundColor(): string {
    return '#f8fafc';
  }

  onAddToCart(product: any): void {
    this.toastService.show('Vista previa: Agregar al carrito deshabilitado en panel.', 'info');
  }

  setDashboardTab(tab: 'stats' | 'products' | 'orders' | 'chats' | 'reviews'): void {
    this.dashboardTab = tab;
    this.openChatId = null;
    this.showProductsView = (tab === 'products');
    if (tab === 'orders') {
      this.loadSellerOrders();
    } else if (tab === 'chats') {
      this.loadSellerChats();
    } else if (tab === 'reviews') {
      this.loadSellerReviews();
    }
  }

  loadSellerOrders(): void {
    this.ordersLoading = true;
    this.sellerService.getSellerOrders().subscribe({
      next: (orders) => {
        this.sellerOrders = orders;
        this.ordersLoading = false;
      },
      error: (err) => {
        console.error('Error loading seller orders:', err);
        this.ordersLoading = false;
      }
    });
  }

  loadSellerChats(): void {
    this.chatsLoading = true;
    this.chatService.getMyChats().subscribe({
      next: (chats) => {
        this.sellerChats = chats.filter(
          (c) => Number(c.seller_id) === Number(this.user?.id)
        );
        this.chatsLoading = false;
      },
      error: (err) => {
        console.error('Error loading seller chats:', err);
        this.chatsLoading = false;
      },
    });
  }

  selectChat(chatId: number): void {
    if (this.openChatId === chatId) {
      this.openChatId = null;
      return;
    }
    this.openChatId = chatId;
    this.chatLoading = true;
    this.chatError = '';
    this.chatMessages = [];
    
    this.chatService.getChatMessages(chatId).subscribe({
      next: (messages) => {
        this.chatMessages = messages;
        this.chatLoading = false;
      },
      error: (err) => {
        console.error('Error loading chat messages:', err);
        this.chatError = 'Error al cargar mensajes.';
        this.chatLoading = false;
      }
    });
  }

  getActiveChat(): any {
    if (!this.openChatId) return null;
    return this.sellerChats.find((c) => c.id === this.openChatId);
  }



  sendChatMessage(): void {
    if (!this.newChatMessage.trim() || !this.openChatId) return;

    const content = this.newChatMessage;
    this.newChatMessage = '';

    this.chatService.sendMessage(this.openChatId, content).subscribe({
      next: (msg) => {
        this.chatMessages.push(msg);
      },
      error: (err) => {
        console.error('Error sending message:', err);
        this.newChatMessage = content;
        
        // Mostrar mensaje de error del backend (como la alerta de seguridad)
        const errorMsg = err.error?.detail || 'No se pudo enviar el mensaje.';
        this.toastService.show(errorMsg, 'error');
      }
    });
  }

  isMyMessage(message: any): boolean {
    return Number(message.sender_id) === Number(this.user?.id);
  }

  getStatusLabel(status: string): string {
    const map: Record<string, string> = {
      'pending': 'Pendiente',
      'confirmed': 'Confirmado',
      'completed': 'Completado',
      'canceled': 'Cancelado'
    };
    return map[status] || status;
  }

  getStatusClass(status: string): string {
    const map: Record<string, string> = {
      'pending': 'bg-amber-100 text-amber-800',
      'confirmed': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'canceled': 'bg-red-100 text-red-800'
    };
    return map[status] || 'bg-slate-100 text-slate-700';
  }

  formatTime(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-PE', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  copyCode(code: string): void {
    navigator.clipboard.writeText(code);
    this.toastService.show('Código copiado al portapapeles', 'success');
  }

  cancelOrder(orderId: number): void {
    this.openConfirmModal(
      'Cancelar Pedido',
      '¿Estás seguro de que deseas cancelar este pedido? Se le notificará al cliente y se le reembolsará el dinero dentro de las próximas 24 horas.',
      () => {
        this.sellerService.cancelSellerOrder(orderId).subscribe({
          next: (response) => {
            this.toastService.show('Pedido cancelado exitosamente.', 'success');
            this.loadSellerOrders();
          },
          error: (error) => {
            console.error('Error cancelling order:', error);
            const errorMsg = error.error?.detail || 'Error al cancelar el pedido. Intenta nuevamente.';
            this.toastService.show(errorMsg, 'error');
          }
        });
      }
    );
  }

  openConfirmModal(title: string, message: string, action: () => void): void {
    this.confirmModalTitle = title;
    this.confirmModalMessage = message;
    this.confirmActionCallback = action;
    this.showConfirmModal = true;
  }

  closeConfirmModal(): void {
    this.showConfirmModal = false;
    this.confirmActionCallback = null;
  }

  executeConfirmAction(): void {
    if (this.confirmActionCallback) {
      this.confirmActionCallback();
    }
    this.closeConfirmModal();
  }

  getFilteredOrders(): any[] {
    if (this.ordersFilter === 'all') {
      return this.sellerOrders;
    } else if (this.ordersFilter === 'pending') {
      return this.sellerOrders.filter(o => o.status === 'pending' || o.status === 'confirmed');
    } else if (this.ordersFilter === 'completed') {
      return this.sellerOrders.filter(o => o.status === 'completed');
    } else if (this.ordersFilter === 'canceled') {
      return this.sellerOrders.filter(o => o.status === 'canceled');
    }
    return this.sellerOrders;
  }

  getPaginatedOrders(): any[] {
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
  }

  nextOrdersPage(): void {
    if (this.ordersPage < this.getOrdersTotalPages()) {
      this.ordersPage++;
    }
  }

  prevOrdersPage(): void {
    if (this.ordersPage > 1) {
      this.ordersPage--;
    }
  }

  getOrderCountByStatus(status: 'pending' | 'completed' | 'canceled'): number {
    if (status === 'pending') {
      return this.sellerOrders.filter(o => o.status === 'pending' || o.status === 'confirmed').length;
    }
    return this.sellerOrders.filter(o => o.status === status).length;
  }

  getThemeClass(): string {
    return `theme-${this.storeTheme}`;
  }

  toggleEditStore(): void {
    if (this.isEditingStore) {
      this.isEditingStore = false;
    } else {
      this.editedStore = { ...this.store };
      this.isEditingStore = true;
    }
  }

  saveStoreChanges(): void {
    if (!this.editedStore.name || !this.editedStore.email) {
      this.toastService.show('Por favor, completa el nombre y email de la tienda', 'error');
      return;
    }

    this.isSaving = true;

    this.sellerService.updateStore(this.editedStore).subscribe({
      next: (response) => {
        console.log('Store updated successfully:', response);
        this.store = response;
        this.determineTheme();
        this.isEditingStore = false;
        this.isSaving = false;
        this.toastService.show('Información de la tienda actualizada exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error updating store:', error);
        this.isSaving = false;
        this.toastService.show('Error al actualizar la información de la tienda. Por favor, intenta nuevamente.', 'error');
      }
    });
  }

  toggleAutoConfirm(event: Event): void {
    const input = event.target as HTMLInputElement;
    const autoConfirm = input.checked;
    
    this.sellerService.updateAutoConfirm(autoConfirm).subscribe({
      next: (response) => {
        if (this.store) {
          this.store.auto_confirm_orders = response.auto_confirm_orders;
        }
        this.toastService.show(
          autoConfirm ? 'Confirmación automática activada.' : 'Confirmación automática desactivada.',
          'success'
        );
      },
      error: (err) => {
        console.error('Error toggling auto confirm:', err);
        this.toastService.show('Error al cambiar la confirmación automática.', 'error');
        input.checked = !autoConfirm;
      }
    });
  }

  confirmOrder(orderId: number): void {
    this.openConfirmModal(
      'Confirmar Pedido',
      '¿Estás seguro de que deseas confirmar/aceptar este pedido? El estado cambiará a Aceptado y se le notificará al cliente.',
      () => {
        this.sellerService.confirmSellerOrder(orderId).subscribe({
          next: (response) => {
            this.toastService.show('Pedido confirmado exitosamente.', 'success');
            this.loadSellerOrders();
          },
          error: (error) => {
            console.error('Error confirming order:', error);
            const errorMsg = error.error?.detail || 'Error al confirmar el pedido. Intenta nuevamente.';
            this.toastService.show(errorMsg, 'error');
          }
        });
      }
    );
  }

  loadSellerReviews(): void {
    if (!this.store?.id) return;
    this.reviewsLoading = true;
    this.reviewService.getStoreReviews(this.store.id).subscribe({
      next: (reviews) => {
        this.sellerReviews = reviews;
        this.reviewsLoading = false;
      },
      error: (err) => {
        console.error('Error loading seller reviews:', err);
        this.reviewsLoading = false;
      }
    });
  }
}

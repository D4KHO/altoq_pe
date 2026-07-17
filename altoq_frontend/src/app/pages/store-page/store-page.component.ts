import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { StoreService, PublicStore } from '../../services/store.service';
import { CartService } from '../../services/cart';
import { AuthService } from '../../services/auth.service';
import { SellerService } from '../../services/seller.service';
import { ProductCard } from '../../components/product-card/product-card';
import { ChatService } from '../../services/chat.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-store-page',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductCard, FormsModule],
  templateUrl: './store-page.component.html',
  styleUrls: ['./store-page.component.css']
})
export class StorePageComponent implements OnInit {
  store: PublicStore | null = null;
  storeProducts: any[] = [];
  isLoading = true;
  errorMessage = '';

  // Live personalization variables
  isEditing = false;
  tempStore: any = null;
  isSaving = false;

  // Formulario de consulta
  inquiryName = '';
  inquiryEmail = '';
  inquiryPhone = '';
  inquiryMessage = '';
  isSendingInquiry = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private storeService: StoreService,
    private cartService: CartService,
    private authService: AuthService,
    private sellerService: SellerService,
    private chatService: ChatService,
    private toastService: ToastService
  ) { }

  ngOnInit(): void {
    const storeId = this.route.snapshot.paramMap.get('id');
    if (storeId) {
      this.loadStore(parseInt(storeId, 10));
    } else {
      this.errorMessage = 'No se especificó una tienda.';
      this.isLoading = false;
    }
  }

  loadStore(storeId: number): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.storeService.getPublicStore(storeId).subscribe({
      next: (store) => {
        this.store = store;
        this.loadStoreProducts(storeId);
      },
      error: () => {
        this.errorMessage = 'No se encontró la tienda o no está disponible.';
        this.isLoading = false;
      }
    });
  }

  loadStoreProducts(storeId: number): void {
    this.storeService.getStoreProducts(storeId).subscribe({
      next: (products) => {
        this.storeProducts = products;
        this.isLoading = false;
      },
      error: () => {
        this.storeProducts = [];
        this.isLoading = false;
      }
    });
  }

  onAddToCart(product: any): void {
    this.cartService.addToCart({
      productId: product.id,
      quantity: 1,
      price: product.price,
      name: product.name,
      image: product.image,
      storeId: product.store_id,
      stock: product.stock
    });
  }

  getThemeGradient(): string {
    const customBgColor = this.isEditing ? this.tempStore?.background_color : this.store?.background_color;
    if (customBgColor && customBgColor !== '#f8fafc' && customBgColor !== '') {
      return customBgColor;
    }

    const themeToUse = this.isEditing ? this.tempStore?.theme : this.store?.theme;
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
    const layout = this.isEditing ? this.tempStore?.layout_type : this.store?.layout_type;
    return `layout-${layout ?? 'grid-3'}`;
  }

  getBackgroundColor(): string {
    return '#f8fafc';
  }

  // Personalization logic
  isOwner(): boolean {
    const user = this.authService.userValue;
    return !!(user && this.store && user.store_id === this.store.id);
  }

  startEditing(): void {
    if (!this.store) return;
    this.tempStore = { ...this.store };
    this.isEditing = true;
  }

  cancelEditing(): void {
    this.isEditing = false;
    this.tempStore = null;
  }

  saveDesignChanges(): void {
    if (!this.tempStore) return;
    this.isSaving = true;
    this.sellerService.updateStore(this.tempStore).subscribe({
      next: (updatedStore) => {
        this.store = {
          ...this.store,
          ...updatedStore
        };
        this.isEditing = false;
        this.tempStore = null;
        this.isSaving = false;
      },
      error: (err) => {
        console.error('Error saving store changes:', err);
        this.isSaving = false;
      }
    });
  }

  onSubmitInquiry(): void {
    if (!this.store) return;
    if (!this.inquiryName || !this.inquiryEmail || !this.inquiryMessage) {
      this.toastService.show('Por favor, completa los campos requeridos.', 'error');
      return;
    }
    this.isSendingInquiry = true;
    this.chatService.sendInquiry(
      this.store.id,
      this.inquiryName,
      this.inquiryEmail,
      this.inquiryPhone,
      this.inquiryMessage
    ).subscribe({
      next: (res) => {
        this.toastService.show('¡Consulta enviada! Se ha creado una cuenta temporal para ti con tu correo.', 'success');
        this.inquiryName = '';
        this.inquiryEmail = '';
        this.inquiryPhone = '';
        this.inquiryMessage = '';
        this.isSendingInquiry = false;
      },
      error: (err) => {
        console.error('Error al enviar consulta:', err);
        const errMsg = err.error?.detail || 'Error al enviar la consulta. Intenta nuevamente.';
        this.toastService.show(errMsg, 'error');
        this.isSendingInquiry = false;
      }
    });
  }
}

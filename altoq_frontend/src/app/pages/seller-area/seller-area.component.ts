import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SellerService } from '../../services/seller.service';
import { ProductService } from '../../services/product.service';
import { ConversationalAssistantComponent } from '../../components/conversational-assistant/conversational-assistant.component';

@Component({
  selector: 'app-seller-area',
  standalone: true,
  imports: [CommonModule, FormsModule, ConversationalAssistantComponent],
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
  currentView: 'store' | 'dashboard' = 'store';
  isEditingStore: boolean = false;
  editedStore: any = {};
  isSaving: boolean = false;
  notification: { show: boolean; message: string; type: 'success' | 'error' } = { show: false, message: '', type: 'success' };
  showProductsView: boolean = false;
  showEditProductModal: boolean = false;
  editingProduct: any = {};
  isSavingProduct: boolean = false;

  constructor(
    private sellerService: SellerService,
    private productService: ProductService
  ) {}

  ngOnInit(): void {
    console.log('SellerAreaComponent initialized');
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
    if (!this.store || !this.store.description) {
      this.storeTheme = 'default';
      return;
    }

    const description = this.store.description.toLowerCase();
    
    if (description.includes('torta') || description.includes('postre') || description.includes('pastel') || description.includes('dulce')) {
      this.storeTheme = 'bakery';
    } else if (description.includes('ropa') || description.includes('moda') || description.includes('vestimenta')) {
      this.storeTheme = 'fashion';
    } else if (description.includes('hogar') || description.includes('jardin') || description.includes('mueble')) {
      this.storeTheme = 'home';
    } else if (description.includes('alimento') || description.includes('comida') || description.includes('bebida')) {
      this.storeTheme = 'food';
    } else if (description.includes('tecnologia') || description.includes('electro') || description.includes('gadget')) {
      this.storeTheme = 'tech';
    } else {
      this.storeTheme = 'default';
    }
  }

  loadStoreProducts(): void {
    this.productService.getProducts().subscribe({
      next: (products) => {
        console.log('Seller Area - All products:', products);
        console.log('Seller Area - Store ID:', this.store?.id);
        console.log('Seller Area - Store:', this.store);

        // Filtrar productos por store_id (manejar string vs number)
        this.storeProducts = products.filter(p => {
          const productStoreId = p.store_id;
          const currentStoreId = this.store?.id;
          console.log(`Seller Area - Comparing product store_id (${productStoreId} type: ${typeof productStoreId}) with store id (${currentStoreId} type: ${typeof currentStoreId})`);
          // Comparar como números para evitar problemas de tipo
          const match = Number(productStoreId) === Number(currentStoreId);
          console.log(`Seller Area - Match result: ${match}`);
          return match;
        });

        console.log('Seller Area - Filtered products:', this.storeProducts);
        console.log('Seller Area - Filtered products count:', this.storeProducts.length);
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
      this.showNotification('Por favor, completa el nombre y precio del producto', 'error');
      return;
    }

    this.isSavingProduct = true;

    this.productService.updateProduct(this.editingProduct.id, this.editingProduct).subscribe({
      next: (response) => {
        console.log('Product updated successfully:', response);
        this.loadStoreProducts();
        this.closeEditModal();
        this.isSavingProduct = false;
        this.showNotification('Producto actualizado exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error updating product:', error);
        this.isSavingProduct = false;
        this.showNotification('Error al actualizar el producto. Por favor, intenta nuevamente.', 'error');
      }
    });
  }

  deleteProduct(productId: number): void {
    if (!confirm('¿Estás seguro de que quieres eliminar este producto?')) {
      return;
    }

    this.productService.deleteProduct(productId).subscribe({
      next: () => {
        console.log('Product deleted successfully');
        this.loadStoreProducts();
        this.showNotification('Producto eliminado exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error deleting product:', error);
        this.showNotification('Error al eliminar el producto. Por favor, intenta nuevamente.', 'error');
      }
    });
  }

  onProductCreated(): void {
    console.log('Product created event received, reloading products...');
    this.loadStoreProducts();
  }

  switchView(view: 'store' | 'dashboard'): void {
    this.currentView = view;
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

  showNotification(message: string, type: 'success' | 'error'): void {
    this.notification = { show: true, message, type };
    setTimeout(() => {
      this.notification.show = false;
    }, 4000);
  }

  saveStoreChanges(): void {
    if (!this.editedStore.name || !this.editedStore.email) {
      this.showNotification('Por favor, completa el nombre y email de la tienda', 'error');
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
        this.showNotification('Información de la tienda actualizada exitosamente', 'success');
      },
      error: (error) => {
        console.error('Error updating store:', error);
        this.isSaving = false;
        this.showNotification('Error al actualizar la información de la tienda. Por favor, intenta nuevamente.', 'error');
      }
    });
  }
}

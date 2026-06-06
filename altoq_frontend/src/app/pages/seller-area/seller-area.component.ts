import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SellerService } from '../../services/seller.service';
import { ProductService } from '../../services/product.service';
import { ConversationalAssistantComponent } from '../../components/conversational-assistant/conversational-assistant.component';

@Component({
  selector: 'app-seller-area',
  standalone: true,
  imports: [CommonModule, ConversationalAssistantComponent],
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
        this.storeProducts = products.filter(p => p.store_id === this.store?.id);
      },
      error: (error) => {
        console.error('Error loading products:', error);
      }
    });
  }

  toggleAddProductChat(): void {
    this.showAddProductChat = !this.showAddProductChat;
  }

  switchView(view: 'store' | 'dashboard'): void {
    this.currentView = view;
  }

  getThemeClass(): string {
    return `theme-${this.storeTheme}`;
  }
}

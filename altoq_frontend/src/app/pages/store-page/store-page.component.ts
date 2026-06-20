import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { StoreService, PublicStore } from '../../services/store.service';
import { CartService } from '../../services/cart';
import { ProductCard } from '../../components/product-card/product-card';

@Component({
  selector: 'app-store-page',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductCard],
  templateUrl: './store-page.component.html',
  styleUrls: ['./store-page.component.css']
})
export class StorePageComponent implements OnInit {
  store: PublicStore | null = null;
  storeProducts: any[] = [];
  isLoading = true;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private storeService: StoreService,
    private cartService: CartService
  ) {}

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
      image: product.image
    });
  }

  getThemeGradient(): string {
    const gradients: Record<string, string> = {
      bakery: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
      fashion: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      home: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      food: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      tech: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      default: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    };
    return gradients[this.store?.theme ?? 'default'] ?? gradients['default'];
  }
}

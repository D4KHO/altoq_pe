import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { SellerService } from '../../services/seller.service';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-store-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './store-page.component.html',
  styleUrls: ['./store-page.component.css']
})
export class StorePageComponent implements OnInit {
  store: any = null;
  storeProducts: any[] = [];
  isLoading = false;
  errorMessage = '';
  storeTheme: string = 'default';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private sellerService: SellerService,
    private productService: ProductService
  ) {}

  ngOnInit(): void {
    const storeId = this.route.snapshot.paramMap.get('id');
    if (storeId) {
      this.loadStore(parseInt(storeId));
    } else {
      this.loadMyStore();
    }
  }

  loadStore(storeId: number): void {
    this.isLoading = true;
    // Aquí necesitarías un endpoint para obtener una tienda por ID
    // Por ahora, usamos getMyStore como fallback
    this.loadMyStore();
  }

  loadMyStore(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.sellerService.getMyStore().subscribe({
      next: (response) => {
        this.store = response;
        this.determineTheme();
        this.loadStoreProducts();
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = error.error?.detail || 'Error al cargar la tienda';
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
    // Aquí necesitarías un endpoint para obtener productos de una tienda específica
    // Por ahora, cargamos todos los productos (esto se debe mejorar)
    this.productService.getProducts().subscribe({
      next: (products) => {
        this.storeProducts = products;
      },
      error: (error) => {
        console.error('Error loading products:', error);
      }
    });
  }

  getThemeClass(): string {
    return `theme-${this.storeTheme}`;
  }
}

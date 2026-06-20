import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './product-detail.html',
  styleUrl: './product-detail.css',
})
export class ProductDetailComponent implements OnInit {
  Object = Object; // Expose Object constructor to template
  product?: Product;
  loading = true;
  error?: string;
  selectedImage: string | null = null;
  selectedColor: string | null = null;
  quantity: number = 1;
  showAllSpecs: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService,
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    const id = idParam ? Number(idParam) : NaN;

    if (!id) {
      this.error = 'Producto no encontrado';
      this.loading = false;
      return;
    }

    this.productService.getProductById(id).subscribe({
      next: (product) => {
        this.product = product;
        if (product) {
          this.selectedImage = product.image;
          
          // TODO: Remove this test code once backend supports multiple images
          if (product.id === 1) {
             this.product.images = [
               product.image,
               'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60' // Image from Laptop
             ];
             // Mock colors for testing
             this.product.colors = ['Negro', 'Plata', 'Azul'];
             this.product.sales = 25; // Test > 20
          } else {
             // Default single color if none exists
             this.product.colors = ['Estándar'];
             this.product.sales = 15; // Test <= 20
          }
          
          if (this.product.colors && this.product.colors.length > 0) {
            this.selectedColor = this.product.colors[0];
          }
        }
        this.loading = false;
      },
      error: () => {
        this.error = 'No se pudo cargar el producto';
        this.loading = false;
      },
    });
  }

  selectImage(image: string) {
    this.selectedImage = image;
  }
  
  selectColor(color: string) {
    this.selectedColor = color;
  }

  incrementQuantity() {
    if (this.product && this.quantity < this.product.stock) {
      this.quantity++;
    }
  }

  decrementQuantity() {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }

  get galleryImages(): string[] {
    if (!this.product) return [];
    if (this.product.images && this.product.images.length > 0) {
      return this.product.images;
    }
    // Fallback: use main image if no gallery exists
    return this.product.image ? [this.product.image] : []; 
  }

  addToCart(): void {
    if (!this.product) return;

    this.cartService.addToCart({
      productId: this.product.id,
      quantity: this.quantity,
      price: this.product.price,
      name: this.product.name,
      image: this.product.image
      // Note: Color is not yet supported by CartItem interface, but is tracked locally
    });
    
    // Optional: Feedback to user about color
    // (CartService already shows a toast message for the basic item)
  }

  getStars(): number[] {
    if (!this.product) return [];
    const stars = [];
    let rating = this.product.rating || 0;
    for (let i = 0; i < 5; i++) {
        if (rating >= 1) {
            stars.push(1);
            rating--;
        } else if (rating >= 0.5) {
            stars.push(0.5);
            rating = 0;
        } else {
            stars.push(0);
        }
    }
    return stars;
  }

  toggleSpecs(): void {
    this.showAllSpecs = !this.showAllSpecs;
  }

  get visibleSpecs(): [string, string][] {
    if (!this.product?.specifications) return [];
    
    const entries = Object.entries(this.product.specifications);
    if (this.showAllSpecs || entries.length <= 4) {
      return entries;
    }
    return entries.slice(0, 4);
  }

  get hasMoreSpecs(): boolean {
    if (!this.product?.specifications) return false;
    return Object.keys(this.product.specifications).length > 4;
  }
}

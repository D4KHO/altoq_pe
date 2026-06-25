import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Observable, catchError, of, map } from 'rxjs';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart';
import { ProductCard } from '../../components/product-card/product-card';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ProductCard, RouterLink],
  templateUrl: './home.html',
  styleUrls: ['./home.css'],
})
export class HomeComponent {
  products$!: Observable<Product[]>;
  error?: string;

  constructor(
    private productService: ProductService,
    private cartService: CartService
  ) {
    this.products$ = this.productService.getProducts().pipe(
      map(products => products.slice(0, 3)), // Mostrar solo 3 productos destacados
      catchError(() => {
        this.error = 'No se pudieron cargar los productos';
        return of([]);
      })
    );
  }

  onAddToCart(product: Product): void {
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
}

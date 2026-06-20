import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable, catchError, of } from 'rxjs';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart';
import { ProductCard } from '../../components/product-card/product-card';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, ProductCard],
  templateUrl: './products.html',
  styleUrl: './products.css',
})
export class Products {
  products$!: Observable<Product[]>;
  error?: string;

  constructor(
    private productService: ProductService,
    private cartService: CartService
  ) {
    this.products$ = this.productService.getProducts().pipe(
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
      image: product.image
    });
  }
}

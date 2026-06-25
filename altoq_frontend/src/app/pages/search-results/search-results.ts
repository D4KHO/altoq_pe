import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { Product } from '../../models/product';
import { ProductCard } from '../../components/product-card/product-card';
import { CartService } from '../../services/cart';
import { Observable, switchMap, map } from 'rxjs';

@Component({
  selector: 'app-search-results',
  standalone: true,
  imports: [CommonModule, ProductCard],
  templateUrl: './search-results.html',
  styleUrl: './search-results.css'
})
export class SearchResultsComponent implements OnInit {
  products$: Observable<Product[]> | undefined;
  query$: Observable<string> | undefined;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService
  ) {}

  ngOnInit(): void {
    this.query$ = this.route.queryParams.pipe(
      map(params => params['q'] || '')
    );

    this.products$ = this.route.queryParams.pipe(
      switchMap(params => {
        const query = params['q'] || '';
        return this.productService.searchProducts(query);
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

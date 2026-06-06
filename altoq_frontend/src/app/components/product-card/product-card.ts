import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Product } from '../../models/product';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './product-card.html',
  styleUrl: './product-card.css',
})
export class ProductCard {
  @Input() product!: Product;
  @Output() addToCart = new EventEmitter<Product>();

  constructor(private router: Router) {}

  goToDetail(event: MouseEvent): void {
    // Si el click fue en el botón de agregar, no navegar
    if ((event.target as HTMLElement).closest('button')) {
      return;
    }
    this.router.navigate(['/products', this.product.id]);
  }

  onAddToCart(event?: MouseEvent): void {
    if (event) {
      event.stopPropagation();
    }
    this.addToCart.emit(this.product);
  }

  goToStore(event: MouseEvent): void {
    event.stopPropagation();
    if (this.product.store_id) {
      this.router.navigate(['/store', this.product.store_id]);
    }
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
}

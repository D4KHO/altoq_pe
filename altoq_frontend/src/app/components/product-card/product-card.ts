import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Product } from '../../models/product';
import { FavoritesService } from '../../services/favorites.service';

@Component({
  selector: 'app-product-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './product-card.html',
  styleUrl: './product-card.css',
})
export class ProductCard implements OnInit {
  @Input() product!: Product;
  @Output() addToCart = new EventEmitter<Product>();

  isFav = false;
  selectedImage: string | null = null;
  featurePills: string[] = [];

  constructor(private router: Router, private favoritesService: FavoritesService) {}

  ngOnInit(): void {
    this.isFav = this.favoritesService.isFavorite(this.product.id);
    // Build feature pills from specifications (max 4)
    if (this.product.specifications) {
      this.featurePills = Object.values(this.product.specifications).slice(0, 4);
    }
  }

  goToDetail(event: MouseEvent): void {
    if ((event.target as HTMLElement).closest('button')) return;
    this.router.navigate(['/products', this.product.id]);
  }

  onAddToCart(event?: MouseEvent): void {
    if (event) event.stopPropagation();
    if (this.product.stock <= 0 || this.product.stock === null) return;
    this.addToCart.emit(this.product);
  }

  goToStore(event: MouseEvent): void {
    event.stopPropagation();
    if (this.product.store_id) {
      this.router.navigate(['/store', this.product.store_id]);
    }
  }

  toggleFavorite(event: MouseEvent): void {
    event.stopPropagation();
    this.isFav = this.favoritesService.toggle(this.product);
  }

  selectImage(event: MouseEvent, img: string): void {
    event.stopPropagation();
    this.selectedImage = img;
  }

  getStars(): number[] {
    if (!this.product) return [];
    const stars = [];
    let rating = this.product.rating || 0;
    for (let i = 0; i < 5; i++) {
      if (rating >= 1) { stars.push(1); rating--; }
      else if (rating >= 0.5) { stars.push(0.5); rating = 0; }
      else { stars.push(0); }
    }
    return stars;
  }
}

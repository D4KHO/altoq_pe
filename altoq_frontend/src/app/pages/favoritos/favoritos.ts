import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FavoritesService } from '../../services/favorites.service';
import { Product } from '../../models/product';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-favoritos',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './favoritos.html',
  styleUrl: './favoritos.css'
})
export class FavoritosComponent implements OnInit {
  favorites: Product[] = [];

  constructor(
    private favoritesService: FavoritesService,
    private toastService: ToastService
  ) {}

  ngOnInit() {
    this.loadFavorites();
  }

  loadFavorites() {
    this.favorites = this.favoritesService.getAll();
  }

  removeFromFavorites(productId: number) {
    this.favoritesService.remove(productId);
    this.loadFavorites();
    this.toastService.show('Producto eliminado de favoritos', 'info');
  }

  getStarsForProduct(product: Product): number[] {
    const stars = [];
    let rating = product.rating || 0;
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

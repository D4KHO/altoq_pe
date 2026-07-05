import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Product } from '../models/product';

const FAVORITES_KEY = 'altoq_favorites';

@Injectable({
  providedIn: 'root'
})
export class FavoritesService {
  private favoritesSubject = new BehaviorSubject<Product[]>(this.load());
  favorites$ = this.favoritesSubject.asObservable();

  private load(): Product[] {
    try {
      const raw = localStorage.getItem(FAVORITES_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  private save(products: Product[]): void {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(products));
    this.favoritesSubject.next(products);
  }

  isFavorite(productId: number): boolean {
    return this.favoritesSubject.value.some(p => p.id === productId);
  }

  toggle(product: Product): boolean {
    const current = this.favoritesSubject.value;
    const exists = current.some(p => p.id === product.id);
    if (exists) {
      this.save(current.filter(p => p.id !== product.id));
      return false; // removed
    } else {
      this.save([...current, product]);
      return true; // added
    }
  }

  remove(productId: number): void {
    this.save(this.favoritesSubject.value.filter(p => p.id !== productId));
  }

  getAll(): Product[] {
    return this.favoritesSubject.value;
  }

  get count(): number {
    return this.favoritesSubject.value.length;
  }
}

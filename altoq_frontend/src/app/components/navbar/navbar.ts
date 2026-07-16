import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { CartService } from '../../services/cart';
import { CategoryService } from '../../services/category.service';
import { AuthService } from '../../services/auth.service';
import { SellerService } from '../../services/seller.service';
import { Category } from '../../models/category';
import { CategoryIconComponent } from '../category-icon/category-icon';
import { User } from '../../models/auth';
import { Observable, map, of } from 'rxjs';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, RouterLinkActive, CategoryIconComponent],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class NavbarComponent implements OnInit {
  itemCount$: Observable<number>;
  categories$!: Observable<Category[]>;
  user$: Observable<User | null>;
  hasStore$: Observable<boolean>;
  showCategoriesDropdown = false;
  showUserDropdown = false;
  searchQuery: string = '';

  constructor(
    private cartService: CartService,
    private router: Router,
    private categoryService: CategoryService,
    private authService: AuthService,
    private sellerService: SellerService
  ) {
    this.itemCount$ = this.cartService.cart$.pipe(
      map(cart => cart.items.reduce((sum, item) => sum + item.quantity, 0))
    );
    this.user$ = this.authService.user$;
    this.hasStore$ = this.authService.user$.pipe(
      map(user => {
        if (!user) return false;
        return !!user.has_store || user.role === 'SELLER' || user.role === 'BOTH';
      })
    );
  }

  ngOnInit() {
    this.categories$ = this.categoryService.getCategories();
    // Refresh current user to get updated role from backend
    if (this.authService.isAuthenticated()) {
      this.authService.refreshCurrentUser().subscribe();
    }
  }

  toggleCategoriesDropdown() {
    this.showCategoriesDropdown = !this.showCategoriesDropdown;
  }

  closeCategoriesDropdown() {
    this.showCategoriesDropdown = false;
  }

  toggleUserDropdown() {
    this.showUserDropdown = !this.showUserDropdown;
  }

  closeUserDropdown() {
    this.showUserDropdown = false;
  }

  logout() {
    this.authService.logout();
    this.closeUserDropdown();
  }

  isAuthPage(): boolean {
    const url = this.router.url;
    return url.includes('/login') || url.includes('/register');
  }

  search(): void {
    if (this.searchQuery.trim()) {
      this.router.navigate(['/search'], { queryParams: { q: this.searchQuery } });
    }
  }
}

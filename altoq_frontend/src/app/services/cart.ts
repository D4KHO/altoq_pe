import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Cart, CartItem } from '../models/cart';
import { AuthService } from './auth.service';
import { ToastService } from './toast.service';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class CartService {
  private cart = new BehaviorSubject<Cart>({ items: [], totalPrice: 0 });
  public cart$ = this.cart.asObservable();

  private cartModalState = new BehaviorSubject<{show: boolean, item: CartItem | null}>({show: false, item: null});
  public cartModalState$ = this.cartModalState.asObservable();

  constructor(
    private authService: AuthService,
    private toastService: ToastService,
    private router: Router
  ) {
    this.authService.user$.subscribe((user) => {
      this.loadCartFromStorage();
      if (user) {
        const pendingItemStr = localStorage.getItem('pending_cart_item');
        if (pendingItemStr) {
          try {
            const pendingItem = JSON.parse(pendingItemStr);
            localStorage.removeItem('pending_cart_item');
            setTimeout(() => {
              this.addToCart(pendingItem);
            }, 100);
          } catch (e) {
            console.error('Error parsing pending cart item', e);
          }
        }
      }
    });
  }

  getCart(): Cart {
    return this.cart.value;
  }

  hideModal(): void {
    this.cartModalState.next({ show: false, item: null });
  }

  addToCart(item: CartItem): void {
    if (!this.authService.isAuthenticated()) {
      localStorage.setItem('pending_cart_item', JSON.stringify(item));
      this.toastService.show('Inicia sesión para agregar productos al carrito', 'info');
      const currentUrl = this.router.url;
      this.router.navigate(['/login'], { queryParams: { returnUrl: currentUrl } });
      return;
    }

    const currentCart = this.cart.value;
    const existingItem = currentCart.items.find(i => i.productId === item.productId);

    if (existingItem) {
      existingItem.quantity += item.quantity;
    } else {
      currentCart.items.push(item);
    }
    this.updateCart(currentCart);
    this.cartModalState.next({ show: true, item: item });
  }

  removeFromCart(productId: number): void {
    const currentCart = this.cart.value;
    currentCart.items = currentCart.items.filter(i => i.productId !== productId);
    this.updateCart(currentCart);
  }

  updateQuantity(productId: number, quantity: number): void {
    const currentCart = this.cart.value;
    const item = currentCart.items.find(i => i.productId === productId);

    if (item) {
      item.quantity = quantity;
      if (item.quantity <= 0) {
        this.removeFromCart(productId);
      } else {
        this.updateCart(currentCart);
      }
    }
  }

  private getCartKey(): string {
    const user = this.authService.userValue;
    if (user && user.email) {
      return `cart_${user.email}`;
    }
    return 'cart_guest';
  }

  clearCart(): void {
    this.cart.next({ items: [], totalPrice: 0 });
    localStorage.removeItem(this.getCartKey());
  }

  private updateCart(cart: Cart): void {
    cart.totalPrice = cart.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    this.cart.next(cart);
    localStorage.setItem(this.getCartKey(), JSON.stringify(cart));
  }

  private loadCartFromStorage(): void {
    const cartData = localStorage.getItem(this.getCartKey());
    if (cartData) {
      this.cart.next(JSON.parse(cartData));
    } else {
      this.cart.next({ items: [], totalPrice: 0 });
    }
  }


}

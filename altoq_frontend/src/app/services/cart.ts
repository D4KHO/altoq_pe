import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Cart, CartItem } from '../models/cart';
import { AuthService } from './auth.service';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root',
})
export class CartService {
  private cart = new BehaviorSubject<Cart>({ items: [], totalPrice: 0 });
  public cart$ = this.cart.asObservable();

  constructor(
    private authService: AuthService,
    private toastService: ToastService
  ) {
    this.authService.user$.subscribe(() => {
      this.loadCartFromStorage();
    });
  }

  getCart(): Cart {
    return this.cart.value;
  }

  addToCart(item: CartItem): void {
    const currentCart = this.cart.value;
    const existingItem = currentCart.items.find(i => i.productId === item.productId);

    if (existingItem) {
      existingItem.quantity += item.quantity;
    } else {
      currentCart.items.push(item);
    }
    this.updateCart(currentCart);
    this.toastService.show(`Se agregó ${item.name} al carrito`, 'success');
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

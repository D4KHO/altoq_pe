import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Cart, CartItem } from '../models/cart';

@Injectable({
  providedIn: 'root',
})
export class CartService {
  private cart = new BehaviorSubject<Cart>({ items: [], totalPrice: 0 });
  public cart$ = this.cart.asObservable();

  constructor() {
    this.loadCartFromStorage();
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

  clearCart(): void {
    this.cart.next({ items: [], totalPrice: 0 });
    localStorage.removeItem('cart');
  }

  private updateCart(cart: Cart): void {
    cart.totalPrice = cart.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    this.cart.next(cart);
    localStorage.setItem('cart', JSON.stringify(cart));
  }

  private loadCartFromStorage(): void {
    const cartData = localStorage.getItem('cart');
    if (cartData) {
      this.cart.next(JSON.parse(cartData));
    }
  }


}

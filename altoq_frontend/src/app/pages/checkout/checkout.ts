import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CartService } from '../../services/cart';
import { OrderService } from '../../services/order';
import { Cart } from '../../models/cart';

@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './checkout.html',
  styleUrl: './checkout.css',
})
export class CheckoutComponent {
  cart: Cart = { items: [], totalPrice: 0 };
  name: string = '';
  email: string = '';
  address: string = '';
  phone: string = '';
  processing: boolean = false;

  constructor(
    private cartService: CartService,
    private orderService: OrderService,
    private router: Router
  ) {
    this.cartService.cart$.subscribe(cart => {
      this.cart = cart;
    });
  }

  onSubmit(): void {
    if (!this.name || !this.email || !this.address || !this.phone) {
      alert('Por favor completa todos los campos');
      return;
    }

    if (this.cart.items.length === 0) {
      alert('Tu carrito está vacío');
      return;
    }

    this.processing = true;

    const order = {
      id: Date.now(),
      userId: 1,
      products: this.cart.items.map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        price: item.price
      })),
      totalAmount: this.cart.totalPrice,
      status: 'pending' as const,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.orderService.createOrder(order).subscribe({
      next: (response) => {
        alert(`¡Orden creada exitosamente! ID: ${response.id}`);
        this.cartService.clearCart();
        this.router.navigate(['/']);
      },
      error: (err) => {
        console.error('Error al crear orden:', err);
        alert('Error al procesar la orden. Inténtalo nuevamente.');
        this.processing = false;
      }
    });
  }
}

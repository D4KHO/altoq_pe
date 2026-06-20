import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { CartService } from '../../services/cart';
import { CartItem } from '../../models/cart';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-cart-added-modal',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <!-- Overlay -->
    <div *ngIf="showModal" class="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center animate-fade-in" (click)="closeModal()">
      <!-- Modal Content -->
      <div class="bg-white rounded-xl shadow-2xl w-[90%] max-w-md p-6 relative animate-slide-up" (click)="$event.stopPropagation()">
        
        <!-- Close Button -->
        <button (click)="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Header -->
        <div class="flex items-center gap-3 text-green-600 mb-6">
          <div class="bg-green-100 p-2 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 class="text-xl font-bold text-gray-800">¡Agregaste a tu carrito!</h2>
        </div>

        <!-- Product Summary -->
        <div class="flex gap-4 mb-8" *ngIf="addedItem">
          <div class="w-24 h-24 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0 border border-gray-200">
            <img [src]="addedItem.image || 'https://via.placeholder.com/150'" [alt]="addedItem.name" class="w-full h-full object-cover">
          </div>
          <div class="flex flex-col justify-center">
            <h3 class="font-semibold text-gray-800 line-clamp-2">{{ addedItem.name }}</h3>
            <p class="text-gray-500 text-sm mt-1">Cantidad: {{ addedItem.quantity }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col gap-3">
          <a routerLink="/cart" (click)="closeModal()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg text-center transition-colors">
            Ver carrito
          </a>
          <button (click)="closeModal()" class="w-full bg-white hover:bg-gray-50 text-blue-600 border border-blue-600 font-semibold py-3 px-4 rounded-lg transition-colors">
            Seguir comprando
          </button>
        </div>

        <!-- Timer Progress Bar -->
        <div class="absolute bottom-0 left-0 w-full h-1.5 bg-gray-100 rounded-b-xl overflow-hidden">
          <div class="h-full bg-blue-600 animate-timer-progress"></div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px) scale(0.95); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .animate-fade-in {
      animation: fadeIn 0.2s ease-out forwards;
    }
    .animate-slide-up {
      animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes timerProgress {
      from { width: 100%; }
      to { width: 0%; }
    }
    .animate-timer-progress {
      animation: timerProgress 2.5s linear forwards;
    }
  `]
})
export class CartAddedModalComponent implements OnInit, OnDestroy {
  showModal = false;
  addedItem: CartItem | null = null;
  private subscription!: Subscription;
  private timeoutId: any;

  constructor(private cartService: CartService) {}

  ngOnInit() {
    this.subscription = this.cartService.cartModalState$.subscribe(state => {
      this.showModal = state.show;
      this.addedItem = state.item;
      
      if (this.showModal) {
        if (this.timeoutId) clearTimeout(this.timeoutId);
        this.timeoutId = setTimeout(() => {
          this.closeModal();
        }, 2500);
      }
    });
  }

  closeModal() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    this.cartService.hideModal();
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
  }
}

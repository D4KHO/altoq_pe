import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SellerService } from '../../services/seller.service';
import { AuthService } from '../../services/auth.service';
import { StoreAssistantComponent } from '../../components/store-assistant/store-assistant.component';

@Component({
  selector: 'app-become-seller',
  standalone: true,
  imports: [CommonModule, FormsModule, StoreAssistantComponent],
  templateUrl: './become-seller.component.html',
  styleUrls: ['./become-seller.component.css']
})
export class BecomeSellerComponent {
  useChatMode: boolean = false;
  storeData = {
    name: '',
    email: '',
    owner_name: '',
    phone: '',
    description: '',
    ruc: ''
  };
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private sellerService: SellerService,
    private router: Router,
    private authService: AuthService
  ) {}

  toggleMode(): void {
    this.useChatMode = !this.useChatMode;
  }

  onSubmit(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.sellerService.becomeSeller(this.storeData).subscribe({
      next: (response) => {
        this.successMessage = '¡Tienda creada exitosamente! Ahora eres vendedor.';
        this.isLoading = false;
        
        // Update user role to BOTH since backend updates it
        const currentUser = this.authService.userValue;
        if (currentUser) {
          const updatedUser = { ...currentUser, role: 'BOTH' as const, has_store: true };
          this.authService.updateUser(updatedUser);
        }
        
        setTimeout(() => {
          this.router.navigate(['/home']);
        }, 2000);
      },
      error: (error) => {
        this.errorMessage = error.error?.detail || 'Error al crear la tienda. Por favor, intenta nuevamente.';
        this.isLoading = false;
      }
    });
  }

  onCancel(): void {
    this.router.navigate(['/profile']);
  }
}

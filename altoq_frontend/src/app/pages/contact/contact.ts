import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contact.html',
  styleUrls: ['./contact.css'],
})
export class ContactComponent {
  name: string = '';
  email: string = '';
  subject: string = '';
  message: string = '';
  isSubmitting = false;

  constructor(private toastService: ToastService) {}

  onSubmit(): void {
    if (!this.name || !this.email || !this.subject || !this.message) {
      this.toastService.show('Por favor, completa todos los campos requeridos.', 'error');
      return;
    }

    this.isSubmitting = true;

    // Simulate sending (replace with real API call if needed)
    setTimeout(() => {
      this.toastService.show('¡Mensaje enviado! Te responderemos a la brevedad.', 'success');
      this.name = '';
      this.email = '';
      this.subject = '';
      this.message = '';
      this.isSubmitting = false;
    }, 1000);
  }
}

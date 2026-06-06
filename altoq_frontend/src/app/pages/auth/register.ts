import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';
import { User } from '../../models/user';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class RegisterComponent {
  name = '';
  email = '';
  password = '';
  address = '';
  phone = '';
  loading = false;
  error?: string;

  constructor(private authService: Auth, private router: Router) {}

  onSubmit(): void {
    if (!this.name || !this.email || !this.password) {
      this.error = 'Completa nombre, correo y contraseña';
      return;
    }

    this.error = undefined;
    this.loading = true;

    const payload: User = {
      id: 0,
      name: this.name,
      email: this.email,
      password: this.password,
      address: this.address,
      phone: this.phone,
      createdAt: new Date(),
    };

    this.authService.register(payload).subscribe({
      next: ({ token, user }) => {
        this.authService.setToken(token, user);
        this.loading = false;
        this.router.navigate(['/']);
      },
      error: () => {
        this.error = 'No se pudo registrar. Inténtalo de nuevo';
        this.loading = false;
      },
    });
  }
}

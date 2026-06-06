import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error?: string;

  constructor(private authService: Auth, private router: Router) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = 'Ingresa tu correo y contraseña';
      return;
    }

    this.error = undefined;
    this.loading = true;

    this.authService.login(this.email, this.password).subscribe({
      next: ({ token, user }) => {
        this.authService.setToken(token, user);
        this.loading = false;
        this.router.navigate(['/']);
      },
      error: () => {
        this.error = 'Credenciales inválidas';
        this.loading = false;
      },
    });
  }
}

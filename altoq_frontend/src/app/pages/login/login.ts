import { Component, OnInit, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { environment } from '../../../environments/environment.development';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private ngZone: NgZone,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // @ts-ignore
    if (typeof google !== 'undefined' && google.accounts) {
      // @ts-ignore
      google.accounts.id.initialize({
        client_id: environment.googleClientId,
        callback: (resp: any) => this.handleGoogleLogin(resp)
      });
      // ...
      // @ts-ignore
      google.accounts.id.renderButton(
        document.getElementById("google-btn"),
        { theme: "outline", size: "large", width: "350" }
      );
    }
  }

  handleGoogleLogin(response: any) {
    this.ngZone.run(() => {
      this.loading = true;
      this.authService.googleLogin(response.credential).subscribe({
        next: () => {
          this.loading = false;
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
          this.router.navigateByUrl(returnUrl);
        },
        error: (err) => {
          this.error = err.error?.detail || 'Error al iniciar sesión con Google';
          this.loading = false;
        }
      });
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        this.loading = false;
        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
        this.router.navigateByUrl(returnUrl);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al iniciar sesión';
        this.loading = false;
      }
    });
  }
}

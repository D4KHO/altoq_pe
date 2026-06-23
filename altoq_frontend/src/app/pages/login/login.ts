import { Component, OnInit, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../services/toast.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  forgotForm: FormGroup;
  verifyForm: FormGroup;
  resetForm: FormGroup;
  
  viewState: 'login' | 'forgot' | 'verify' | 'reset' = 'login';
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private ngZone: NgZone,
    private router: Router,
    private route: ActivatedRoute,
    private toastService: ToastService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });

    this.forgotForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]]
    });

    this.verifyForm = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(7)]]
    });

    this.resetForm = this.fb.group({
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, { validators: this.passwordsMatchValidator });
  }

  passwordsMatchValidator(group: FormGroup) {
    const pass = group.get('newPassword')?.value;
    const confirmPass = group.get('confirmPassword')?.value;
    return pass === confirmPass ? null : { notMatching: true };
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
          this.toastService.show('¡Bienvenido a ALTOQ!', 'success');
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
          this.router.navigateByUrl(returnUrl);
        },
        error: (err) => {
          this.error = err.error?.detail || 'Error al iniciar sesión con Google';
          this.toastService.show(this.error, 'error');
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
        this.toastService.show('¡Bienvenido a ALTOQ!', 'success');
        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
        this.router.navigateByUrl(returnUrl);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al iniciar sesión';
        this.toastService.show(this.error, 'error');
        this.loading = false;
      }
    });
  }

  changeState(state: 'login' | 'forgot' | 'verify' | 'reset') {
    this.viewState = state;
    this.error = '';
    
    if (state === 'login') {
      this.forgotForm.reset();
      this.verifyForm.reset();
      this.resetForm.reset();
    } else if (state === 'forgot') {
      // Auto-populate email from login form if filled
      const loginEmail = this.loginForm.get('email')?.value;
      if (loginEmail) {
        this.forgotForm.patchValue({ email: loginEmail });
      }
    }
  }

  onForgotPasswordSubmit(): void {
    if (this.forgotForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.forgotPassword(this.forgotForm.value.email).subscribe({
      next: () => {
        this.loading = false;
        this.toastService.show('Código de recuperación enviado con éxito', 'success');
        this.changeState('verify');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al enviar código de recuperación';
        this.toastService.show(this.error, 'error');
        this.loading = false;
      }
    });
  }

  onVerifyCodeSubmit(): void {
    if (this.verifyForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.verifyCode(this.forgotForm.value.email, this.verifyForm.value.code).subscribe({
      next: () => {
        this.loading = false;
        this.toastService.show('Código verificado con éxito', 'success');
        this.changeState('reset');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Código incorrecto o expirado';
        this.toastService.show(this.error, 'error');
        this.loading = false;
      }
    });
  }

  onResetPasswordSubmit(): void {
    if (this.resetForm.invalid) {
      return;
    }

    this.loading = true;
    this.error = '';

    this.authService.resetPassword(
      this.forgotForm.value.email,
      this.verifyForm.value.code,
      this.resetForm.value.newPassword
    ).subscribe({
      next: () => {
        this.loading = false;
        this.toastService.show('¡Contraseña actualizada con éxito!', 'success');
        this.loginForm.patchValue({ email: this.forgotForm.value.email, password: '' });
        this.changeState('login');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al cambiar la contraseña';
        this.toastService.show(this.error, 'error');
        this.loading = false;
      }
    });
  }
}

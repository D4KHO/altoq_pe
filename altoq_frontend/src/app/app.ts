import { Component, signal, inject } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { NavbarComponent } from './components/navbar/navbar';
import { ToastComponent } from './components/toast/toast';
import { CartAddedModalComponent } from './components/cart-added-modal/cart-added-modal.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, NavbarComponent, ToastComponent, CartAddedModalComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('altoq_frontend');
  protected readonly showNavbar = signal(true);

  constructor() {
    const router = inject(Router);
    // Escuchar eventos de navegación para saber si ocultar la barra de usuario
    router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const url = event.urlAfterRedirects || event.url;
      this.showNavbar.set(!url.startsWith('/admin'));
    });
  }
}

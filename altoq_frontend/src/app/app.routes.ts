import { inject } from '@angular/core';
import { Routes, Router } from '@angular/router';
import { AdminAuthService } from './services/admin-auth';
import { CartComponent } from './pages/cart/cart';
import { CheckoutComponent } from './pages/checkout/checkout';
import { ProductDetailComponent } from './pages/product-detail/product-detail';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/home/home').then((m) => m.HomeComponent),
  },
  {
    path: 'products',
    loadComponent: () =>
      import('./pages/products/products').then((m) => m.Products),
  },
  {
    path: 'contacto',
    loadComponent: () =>
      import('./pages/contact/contact').then((m) => m.ContactComponent),
  },
  {
    path: 'marcas',
    loadComponent: () =>
      import('./pages/marcas/marcas').then((m) => m.MarcasComponent),
  },
  {
    path: 'nosotros',
    loadComponent: () =>
      import('./pages/nosotros/nosotros').then((m) => m.NosotrosComponent),
  },
  {
    path: 'terminos',
    loadComponent: () =>
      import('./pages/terminos/terminos').then((m) => m.TerminosComponent),
  },
  {
    path: 'privacidad',
    loadComponent: () =>
      import('./pages/privacidad/privacidad').then((m) => m.PrivacidadComponent),
  },
  {
    path: 'favoritos',
    loadComponent: () =>
      import('./pages/favoritos/favoritos').then((m) => m.FavoritosComponent),
  },
  {
    path: 'faq',
    loadComponent: () =>
      import('./pages/faq/faq').then((m) => m.FaqComponent),
  },
  {
    path: 'products/:id',
    loadComponent: () =>
      import('./pages/product-detail/product-detail').then(
        (m) => m.ProductDetailComponent
      ),
  },
  {
    path: 'cart',
    loadComponent: () =>
      import('./pages/cart/cart').then((m) => m.CartComponent),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./pages/login/login').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./pages/register/register').then((m) => m.RegisterComponent),
  },
  {
    path: 'category/:slug',
    loadComponent: () =>
      import('./pages/category/category').then((m) => m.CategoryComponent),
  },
  {
    path: 'search',
    loadComponent: () =>
      import('./pages/search-results/search-results').then((m) => m.SearchResultsComponent),
  },
  {
    path: 'checkout',
    loadComponent: () =>
      import('./pages/checkout/checkout').then((m) => m.CheckoutComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./pages/profile/profile').then((m) => m.ProfileComponent),
    canActivate: [authGuard]
  },
  {
    path: 'my-orders',
    loadComponent: () =>
      import('./pages/my-orders/my-orders.component').then((m) => m.MyOrdersComponent),
    canActivate: [authGuard]
  },
  {
    path: 'my-orders/:id',
    loadComponent: () =>
      import('./pages/order-detail/order-detail.component').then((m) => m.OrderDetailComponent),
    canActivate: [authGuard]
  },
  {
    path: 'become-seller',
    loadComponent: () =>
      import('./pages/become-seller/become-seller.component').then((m) => m.BecomeSellerComponent),
    canActivate: [authGuard]
  },
  {
    path: 'seller-area',
    loadComponent: () =>
      import('./pages/seller-area/seller-area.component').then((m) => m.SellerAreaComponent),
    canActivate: [authGuard]
  },
  {
    path: 'store/:id',
    loadComponent: () =>
      import('./pages/store-page/store-page.component').then((m) => m.StorePageComponent),
  },
  {
    path: 'my-store',
    loadComponent: () =>
      import('./pages/store-page/store-page.component').then((m) => m.StorePageComponent),
    canActivate: [authGuard]
  },
  {
    path: 'delivery/manage/:id',
    loadComponent: () =>
      import('./pages/delivery-manage/delivery-manage.component').then((m) => m.DeliveryManageComponent),
    canActivate: [authGuard]
  },
  {
    path: 'delivery/track/:token',
    loadComponent: () =>
      import('./pages/delivery-track/delivery-track.component').then((m) => m.DeliveryTrackComponent),
  },
  // Admin routes
  {
    path: 'admin/login',
    loadComponent: () =>
      import('./pages/admin/login/login').then((m) => m.Login),
  },
  {
    path: 'admin',
    loadComponent: () =>
      import('./pages/admin/dashboard/dashboard').then((m) => m.Dashboard),
    canActivate: [() => inject(AdminAuthService).isAuthenticated() || inject(Router).createUrlTree(['/admin/login'])],
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'dashboard'
      },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./pages/admin/metrics-dashboard/metrics-dashboard').then((m) => m.MetricsDashboard),
      },
      {
        path: 'users',
        loadComponent: () =>
          import('./pages/admin/users/users').then((m) => m.Users),
      },
      {
        path: 'stores',
        loadComponent: () =>
          import('./pages/admin/stores/stores').then((m) => m.Stores),
      },
    ]
  },
];

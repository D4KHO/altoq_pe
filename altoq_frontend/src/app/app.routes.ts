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
          import('./pages/admin/users/users').then((m) => m.Users), // Temporary: show users on dashboard
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

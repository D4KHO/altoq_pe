import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AdminAuthService } from '../../../services/admin-auth';
import { Observable } from 'rxjs';

interface AdminResponse {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
}

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard {
  admin$: Observable<AdminResponse | null>;

  constructor(private adminAuthService: AdminAuthService, private router: Router) {
    this.admin$ = this.adminAuthService.admin$;
  }

  logout(): void {
    this.adminAuthService.logout();
  }
}

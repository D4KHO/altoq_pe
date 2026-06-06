import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AdminAuthService } from '../../../services/admin-auth';

interface User {
  id: number;
  email: string;
  name: string;
  phone: string | null;
  address: string | null;
  created_at: string;
}

@Component({
  selector: 'app-users',
  imports: [CommonModule],
  templateUrl: './users.html',
  styleUrl: './users.css'
})
export class Users implements OnInit {
  users: User[] = [];
  isLoading = false;

  constructor(private http: HttpClient, private authService: AdminAuthService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<User[]>('http://localhost:8000/api/admin/users/', { headers }).subscribe({
      next: (users) => {
        this.users = users;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.isLoading = false;
      }
    });
  }

  deleteUser(userId: number): void {
    if (!confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`http://localhost:8000/api/admin/users/${userId}`, { headers }).subscribe({
      next: () => {
        this.users = this.users.filter(u => u.id !== userId);
      },
      error: (error) => {
        console.error('Error deleting user:', error);
        alert('Error al eliminar usuario');
      }
    });
  }
}

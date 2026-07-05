import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AdminAuthService } from '../../../services/admin-auth';
import { environment } from '../../../../environments/environment';

interface User {
  id: number;
  email: string;
  name: string;
  phone: string | null;
  address: string | null;
  created_at: string;
  role: string;
}

interface Address {
  id: number;
  city: string;
  state: string;
  postal_code: string;
  line1: string;
  line2: string | null;
  phone: string;
  is_default: boolean;
}

@Component({
  selector: 'app-users',
  imports: [CommonModule, FormsModule],
  templateUrl: './users.html',
  styleUrl: './users.css'
})
export class Users implements OnInit {
  users: User[] = [];
  isLoading = false;
  
  // Filtros y búsquedas
  searchQuery = '';
  selectedRole = 'all';

  // Control de Modales
  showCreateModal = false;
  showEditModal = false;
  showDetailsModal = false;

  // Formulario Crear Usuario
  newUser = {
    name: '',
    email: '',
    password: '',
    phone: '',
    address: ''
  };

  // Formulario Editar Usuario
  editingUserId: number | null = null;
  editForm = {
    name: '',
    phone: '',
    address: ''
  };

  // Detalles de Usuario
  detailedUser: User | null = null;
  userAddresses: Address[] = [];
  isLoadingAddresses = false;

  constructor(private http: HttpClient, private authService: AdminAuthService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<User[]>(`${environment.apiUrl}/admin/users/`, { headers }).subscribe({
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

  // Filtrado de usuarios dinámico en frontend
  get filteredUsers(): User[] {
    return this.users.filter(user => {
      const matchesSearch = 
        user.name?.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        user.email?.toLowerCase().includes(this.searchQuery.toLowerCase());
      
      const matchesRole = 
        this.selectedRole === 'all' || 
        user.role?.toLowerCase() === this.selectedRole.toLowerCase();

      return matchesSearch && matchesRole;
    });
  }

  // Métodos del Modal de Creación
  openCreateModal(): void {
    this.newUser = { name: '', email: '', password: '', phone: '', address: '' };
    this.showCreateModal = true;
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
  }

  submitCreateUser(): void {
    if (!this.newUser.name || !this.newUser.email || !this.newUser.password) {
      alert('Por favor complete los campos requeridos (Nombre, Email, Contraseña)');
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.post<User>(`${environment.apiUrl}/admin/users/`, this.newUser, { headers }).subscribe({
      next: (createdUser) => {
        this.users.unshift(createdUser); // Añadir al inicio de la tabla
        this.closeCreateModal();
      },
      error: (error) => {
        console.error('Error creating user:', error);
        alert(error?.error?.detail || 'Error al registrar el nuevo usuario.');
      }
    });
  }

  // Métodos del Modal de Edición
  openEditModal(user: User): void {
    this.editingUserId = user.id;
    this.editForm = {
      name: user.name,
      phone: user.phone || '',
      address: user.address || ''
    };
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.editingUserId = null;
  }

  submitEditUser(): void {
    if (!this.editForm.name || !this.editingUserId) {
      alert('Por favor complete el nombre del usuario.');
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.put<User>(`${environment.apiUrl}/admin/users/${this.editingUserId}`, this.editForm, { headers }).subscribe({
      next: (updatedUser) => {
        const index = this.users.findIndex(u => u.id === this.editingUserId);
        if (index !== -1) {
          this.users[index] = updatedUser;
        }
        this.closeEditModal();
      },
      error: (error) => {
        console.error('Error updating user:', error);
        alert(error?.error?.detail || 'Error al actualizar el usuario.');
      }
    });
  }

  // Métodos del Modal de Detalles
  openDetailsModal(user: User): void {
    this.detailedUser = user;
    this.userAddresses = [];
    this.showDetailsModal = true;
    this.loadUserAddresses(user.id);
  }

  closeDetailsModal(): void {
    this.showDetailsModal = false;
    this.detailedUser = null;
  }

  loadUserAddresses(userId: number): void {
    this.isLoadingAddresses = true;
    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<Address[]>(`${environment.apiUrl}/admin/users/${userId}/addresses`, { headers }).subscribe({
      next: (addresses) => {
        this.userAddresses = addresses;
        this.isLoadingAddresses = false;
      },
      error: (error) => {
        console.error('Error loading addresses:', error);
        this.isLoadingAddresses = false;
      }
    });
  }

  deleteUser(userId: number): void {
    if (!confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`${environment.apiUrl}/admin/users/${userId}`, { headers }).subscribe({
      next: () => {
        this.users = this.users.filter(u => u.id !== userId);
      },
      error: (error) => {
        console.error('Error deleting user:', error);
        // Capturar mensaje específico del backend (IntegrityError de FastAPI)
        const errorMessage = error?.error?.detail || 'Error al eliminar usuario';
        alert(errorMessage);
      }
    });
  }
}

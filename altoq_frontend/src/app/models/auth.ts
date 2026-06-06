export interface User {
  id: number;
  email: string;
  name: string;
  address?: string;
  phone?: string;
  is_active: boolean;
  is_admin: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  address?: string;
  phone?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

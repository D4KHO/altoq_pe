export interface Address {
  id: number;
  user_id: number;
  name?: string;
  street: string;
  city: string;
  state?: string;
  postal_code?: string;
  country: string;
  phone?: string;
  is_default: boolean;
  created_at: string;
}

export interface AddressCreate {
  name?: string;
  street: string;
  city: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  is_default?: boolean;
}

export interface AddressUpdate {
  name?: string;
  street?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  is_default?: boolean;
}

export interface UserUpdate {
  name?: string;
  phone?: string;
  address?: string;
}

export interface PasswordChange {
  old_password: string;
  new_password: string;
}

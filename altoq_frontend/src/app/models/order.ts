export interface Order {
  id?: number;
  user_id: number;
  products: OrderItem[];
  total_amount: number;
  status: 'pending' | 'confirmed' | 'completed' | 'canceled' | 'delivering';
  shipping_address: string;
  contact_phone: string;
  delivery_code?: string;
  shipping_latitude?: number;
  shipping_longitude?: number;
  delivery_latitude?: number;
  delivery_longitude?: number;
  delivery_status?: string;
  delivery_token?: string;
  client_name?: string;
  client_email?: string;
  created_at?: Date;
  updated_at?: Date;
}

export interface OrderItem {
  productId: number;
  quantity: number;
  price: number;
}
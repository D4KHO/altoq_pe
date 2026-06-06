export interface Order {
  id: number;
  userId: number;
  products: OrderItem[];
  totalAmount: number;
  status: 'pending' | 'completed' | 'canceled';
  createdAt: Date;
  updatedAt: Date;
}

export interface OrderItem {
  productId: number;
  quantity: number;
  price: number;
}
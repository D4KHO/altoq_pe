export interface Cart {
  items: CartItem[];
  totalPrice: number;
}

export interface CartItem {
  productId: number;
  quantity: number;
  price: number;
  name: string;
  image?: string;
}
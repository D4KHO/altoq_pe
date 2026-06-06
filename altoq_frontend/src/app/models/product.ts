export interface Product {
  id: number;
  name: string;
  price: number;
  description: string;
  image: string;
  category: string;
  store_name?: string;
  store_id?: number;
  rating: number;
  rating_count: number;
  stock: number;
  images?: string[];
  colors?: string[];
  sales?: number;
  specifications?: Record<string, string>;
  created_at: string;
}
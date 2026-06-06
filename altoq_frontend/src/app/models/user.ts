export interface User {
  id: number;
  email: string;
  name: string;
  password?: string;
  address: string;
  phone: string;
  createdAt: Date;
}
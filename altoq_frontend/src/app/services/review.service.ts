import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ReviewCreate {
  product_id: number;
  order_id: number;
  rating: number;
  store_rating: number;
  comment?: string;
  image_url?: string;
}

export interface Review {
  id: number;
  user_id: number;
  user_name?: string;
  product_id: number;
  store_id: number;
  order_id: number;
  rating: number;
  store_rating: number;
  comment?: string;
  image_url?: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class ReviewService {
  private apiUrl = `${environment.apiUrl}/reviews`;

  constructor(private http: HttpClient) {}

  createReview(reviewData: ReviewCreate): Observable<Review> {
    return this.http.post<Review>(`${this.apiUrl}/`, reviewData);
  }

  getProductReviews(productId: number): Observable<Review[]> {
    return this.http.get<Review[]>(`${this.apiUrl}/product/${productId}`);
  }

  getOrderReviews(orderId: number): Observable<Review[]> {
    return this.http.get<Review[]>(`${this.apiUrl}/order/${orderId}`);
  }

  getStoreReviews(storeId: number): Observable<Review[]> {
    return this.http.get<Review[]>(`${this.apiUrl}/store/${storeId}`);
  }

  checkPendingReview(productId: number): Observable<{ can_review: boolean; order_id: number | null }> {
    return this.http.get<{ can_review: boolean; order_id: number | null }>(`${this.apiUrl}/pending-review/product/${productId}`);
  }

  uploadReviewImage(file: File): Observable<{ message: string; image_url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ message: string; image_url: string }>(`${this.apiUrl}/upload`, formData);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Category, CategoryTree, CategoryWithProducts } from '../models/category';

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private apiUrl = 'http://localhost:8000/api/categories/';

  constructor(private http: HttpClient) {}

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(this.apiUrl);
  }

  getCategoryTree(): Observable<CategoryTree[]> {
    return this.http.get<CategoryTree[]>(`${this.apiUrl}tree`);
  }

  getCategoriesWithCounts(): Observable<CategoryWithProducts[]> {
    return this.http.get<CategoryWithProducts[]>(`${this.apiUrl}with-counts`);
  }

  getCategoryById(id: number): Observable<Category> {
    return this.http.get<Category>(`${this.apiUrl}${id}`);
  }

  getCategoryBySlug(slug: string): Observable<Category> {
    return this.http.get<Category>(`${this.apiUrl}slug/${slug}`);
  }

  createCategory(categoryData: any): Observable<any> {
    return this.http.post(this.apiUrl, categoryData);
  }
}

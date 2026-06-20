import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PublicStore {
  id: number;
  name: string;
  owner_name?: string;
  phone?: string;
  description?: string;
  logo?: string;
  ruc?: string;
  theme?: string;
  status?: string;
}

@Injectable({
  providedIn: 'root'
})
export class StoreService {
  private apiUrl = 'http://localhost:8000/api/stores';

  constructor(private http: HttpClient) {}

  getPublicStore(storeId: number): Observable<PublicStore> {
    return this.http.get<PublicStore>(`${this.apiUrl}/${storeId}`);
  }

  getStoreProducts(storeId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${storeId}/products`);
  }
}

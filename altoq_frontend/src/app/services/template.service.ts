import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TemplateService {
  private apiUrl = 'http://localhost:8000/api/templates';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getParams(): any {
    const token = this.authService.getToken();
    return token ? { token } : {};
  }

  createTemplate(templateData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, templateData, {
      params: this.getParams()
    });
  }

  getTemplates(categoryId?: number): Observable<any[]> {
    let params = new HttpParams();
    if (categoryId) {
      params = params.set('category_id', categoryId.toString());
    }
    const tokenParams = this.getParams();
    Object.keys(tokenParams).forEach(key => {
      params = params.set(key, tokenParams[key]);
    });
    return this.http.get<any[]>(`${this.apiUrl}/`, { params });
  }

  getTemplate(templateId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${templateId}`, {
      params: this.getParams()
    });
  }

  detectCategory(productName: string): Observable<any> {
    const params = { ...this.getParams(), product_name: productName };
    return this.http.post(`${this.apiUrl}/detect-category`, null, {
      params
    });
  }

  addTemplateField(templateId: number, fieldData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${templateId}/fields`, fieldData, {
      params: this.getParams()
    });
  }

  getTemplateFields(templateId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${templateId}/fields`, {
      params: this.getParams()
    });
  }
}

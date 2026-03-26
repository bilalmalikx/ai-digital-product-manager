// product.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Product, ProductGenerateRequest, ProductResponse, ProductListResponse } from '../models/product';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = 'http://localhost:8000/products';

  constructor(private http: HttpClient) {}

  generateProduct(request: ProductGenerateRequest): Observable<ProductResponse> {
    return this.http.post<ProductResponse>(`${this.apiUrl}/generate`, request);
  }

  getProducts(skip: number = 0, limit: number = 100): Observable<ProductListResponse> {
    return this.http.get<ProductListResponse>(`${this.apiUrl}/?skip=${skip}&limit=${limit}`);
  }

  getProduct(productId: string): Observable<ProductResponse> {
    return this.http.get<ProductResponse>(`${this.apiUrl}/${productId}`);
  }
}
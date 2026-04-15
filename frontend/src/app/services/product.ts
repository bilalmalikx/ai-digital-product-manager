// product.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Product, ProductGenerateRequest, ProductResponse, ProductListResponse } from '../models/product';

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = 'http://127.0.0.1:8000/products';

  constructor(private http: HttpClient) {}

  // Existing method - simple text input
  generateProduct(request: ProductGenerateRequest): Observable<ProductResponse> {
    return this.http.post<ProductResponse>(`${this.apiUrl}/generate`, request);
  }

  // NEW: Multi-format file upload method
  generateProductFromFiles(formData: FormData): Observable<ProductResponse> {
    return this.http.post<ProductResponse>(`${this.apiUrl}/generate-from-files`, formData);
  }

  // NEW: Streaming with file upload
  generateProductFromFilesStream(formData: FormData): Observable<EventSource> {
    // For streaming, you'll need to implement EventSource or WebSocket
    // This is a placeholder - actual implementation depends on your streaming method
    const eventSource = new EventSource(`${this.apiUrl}/generate-from-files-stream?${new URLSearchParams(formData as any).toString()}`);
    return new Observable(observer => {
      eventSource.onmessage = (event) => {
        observer.next(JSON.parse(event.data));
      };
      eventSource.onerror = (error) => {
        observer.error(error);
        eventSource.close();
      };
      return () => eventSource.close();
    });
  }

  getProducts(skip: number = 0, limit: number = 100): Observable<ProductListResponse> {
    return this.http.get<ProductListResponse>(`${this.apiUrl}/?skip=${skip}&limit=${limit}`);
  }

  getProduct(productId: string): Observable<ProductResponse> {
    return this.http.get<ProductResponse>(`${this.apiUrl}/${productId}`);
  }
}
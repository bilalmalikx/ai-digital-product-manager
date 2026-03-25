import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-list.html',
  styleUrls: ['./product-list.scss']
})
export class ProductList implements OnInit {
  products: Product[] = [];
  isLoading: boolean = true;
  error: string | null = null;
  total: number = 0;
  skip: number = 0;
  limit: number = 10;

  constructor(private productService: ProductService) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.isLoading = true;
    this.productService.getProducts(this.skip, this.limit).subscribe({
      next: (response) => {
        this.products = response.products;
        this.total = response.total;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load products. Please try again.';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  getStatusClass(status: string): string {
    switch(status) {
      case 'draft': return 'status-draft';
      case 'in_review': return 'status-review';
      case 'approved': return 'status-approved';
      case 'rejected': return 'status-rejected';
      default: return 'status-draft';
    }
  }

  getStatusIcon(status: string): string {
    switch(status) {
      case 'draft': return '📝';
      case 'in_review': return '🔍';
      case 'approved': return '✅';
      case 'rejected': return '❌';
      default: return '📌';
    }
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  previousPage(): void {
    if (this.skip > 0) {
      this.skip = Math.max(0, this.skip - this.limit);
      this.loadProducts();
    }
  }

  nextPage(): void {
    if (this.skip + this.limit < this.total) {
      this.skip += this.limit;
      this.loadProducts();
    }
  }

  retry(): void {
    this.error = null;
    this.loadProducts();
  }
}
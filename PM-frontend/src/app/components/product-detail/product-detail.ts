import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.scss']
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  isLoading: boolean = true;
  error: string | null = null;
  activeTab: string = 'overview';

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const productId = params['id'];
      if (productId) {
        this.loadProduct(productId);
      }
    });
  }

  loadProduct(productId: string): void {
    this.isLoading = true;
    this.productService.getProduct(productId).subscribe({
      next: (response: any) => {
        if (response.success && response.data) {
          this.product = response.data;
        } else {
          this.error = response.error || 'Product not found';
        }
        this.isLoading = false;
      },
      error: (err: any) => {
        this.error = 'Failed to load product details';
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
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  setActiveTab(tab: string): void {
    this.activeTab = tab;
  }

  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  }

  downloadPRD(): void {
    if (this.product?.final_prd) {
      const blob = new Blob([this.product.final_prd], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.product.name || 'product'}_prd.md`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  }

  getOutputKeys(output: any): string[] {
    return output ? Object.keys(output) : [];
  }

  formatValue(value: any): string {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  retry(): void {
    this.error = null;
    const productId = this.route.snapshot.params['id'];
    if (productId) {
      this.loadProduct(productId);
    }
  }
}
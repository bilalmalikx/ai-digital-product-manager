// product-detail.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-product-detail',
  imports: [CommonModule, RouterModule],
  templateUrl: './product-detail.html',
  styleUrl: './product-detail.scss'
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  isLoading: boolean = true;
  error: string | null = null;
  activeTab: string = 'overview';
  
  pipelineStages = [
    { name: 'Strategist', key: 'strategist_output' },
    { name: 'Market Research', key: 'market_research_output' },
    { name: 'PRD', key: 'prd_output' },
    { name: 'Tech Architecture', key: 'tech_architecture' },
    { name: 'UX Design', key: 'ux_design' },
    { name: 'QA Strategy', key: 'qa_strategy' }
  ];
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
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
  
  // Add this getter to provide completed stages with 'completed' property
  get completedStages(): { name: string, completed: boolean, key: string }[] {
    if (!this.product) return [];
    return this.pipelineStages.map(stage => ({
      name: stage.name,
      key: stage.key,
      completed: !!this.product?.[stage.key as keyof Product]
    }));
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
      case 'in_review': return 'status-in_review';
      case 'approved': return 'status-approved';
      case 'completed': return 'status-completed';
      case 'rejected': return 'status-rejected';
      default: return 'status-draft';
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
  
  truncateId(id: string): string {
    if (!id) return '';
    return id.length > 18 ? id.substring(0, 18) + '...' : id;
  }
  
  setActiveTab(tab: string): void {
    this.activeTab = tab;
  }
  
  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text).then(() => {
      console.log('Copied to clipboard');
    });
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
  
  formatOutput(output: any): string {
    if (!output) return '';
    return JSON.stringify(output, null, 2);
  }
  
  goBack(): void {
    this.router.navigate(['/products']);
  }
}
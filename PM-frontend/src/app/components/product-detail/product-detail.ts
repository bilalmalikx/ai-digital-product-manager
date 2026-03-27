// product-detail.ts
import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-detail.html',
  styleUrl: './product-detail.scss'
})
export class ProductDetailComponent implements OnInit, OnDestroy {
  product: Product | null = null;
  isLoading: boolean = true;
  error: string | null = null;
  activeTab: string = 'overview';
  private routeSubscription: Subscription | null = null;
  private productId: string = '';
  
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
    private productService: ProductService,
    private cdr: ChangeDetectorRef
  ) {
    console.log('ProductDetailComponent constructor');
  }
  
  ngOnInit(): void {
    console.log('ProductDetailComponent ngOnInit');
    
    // Subscribe to route params changes
    this.routeSubscription = this.route.params.subscribe(params => {
      const newId = params['id'];
      console.log('Route params changed, new ID:', newId);
      
      if (newId && typeof newId === 'string') {
        this.productId = newId;
        this.loadProduct(this.productId);
      } else {
        console.error('No valid product ID in route');
        this.error = 'No product ID provided';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }
  
  ngOnDestroy(): void {
    if (this.routeSubscription) {
      this.routeSubscription.unsubscribe();
      this.routeSubscription = null;
    }
  }
  
  get completedStages(): { name: string, completed: boolean, key: string }[] {
    if (!this.product) return [];
    return this.pipelineStages.map(stage => ({
      name: stage.name,
      key: stage.key,
      completed: !!this.product?.[stage.key as keyof Product]
    }));
  }
  
  loadProduct(productId: string): void {
    console.log('Loading product:', productId);
    this.isLoading = true;
    this.error = null;
    this.product = null;
    this.cdr.detectChanges();
    
    this.productService.getProduct(productId).subscribe({
      next: (response: any) => {
        console.log('Product API response:', response);
        if (response.success && response.data) {
          this.product = response.data;
          console.log('Product loaded successfully:', this.product);
        } else {
          this.error = response.error || 'Product not found';
          console.error('Product not found:', response.error);
        }
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        console.error('Failed to load product details:', err);
        this.error = 'Failed to load product details. Please try again.';
        this.isLoading = false;
        this.cdr.detectChanges();
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
    this.cdr.detectChanges();
  }
  
  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text).then(() => {
      console.log('Copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy:', err);
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
    console.log('Going back to products list');
    this.router.navigate(['/products']).then(success => {
      console.log('Back navigation result:', success);
    }).catch(err => {
      console.error('Back navigation error:', err);
    });
  }
}
// product-list.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { filter, Subscription } from 'rxjs';
import { Product } from '../../models/product';
import { ProductService } from '../../services/product';

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './product-list.html',
  styleUrl: './product-list.scss'
})
export class ProductListComponent implements OnInit, OnDestroy {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  isLoading: boolean = true;
  total: number = 0;
  skip: number = 0;
  limit: number = 12;
  
  searchTerm: string = '';
  statusFilter: string = '';
  private routerSubscription: Subscription;
  
  constructor(private productService: ProductService, private router: Router) {
    // Listen to route changes to reload products when coming back from detail
    this.routerSubscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      if (event.url === '/products') {
        console.log('Returned to products list, reloading...');
        this.loadProducts();
      }
    });
  }
  
  ngOnInit(): void {
    this.loadProducts();
  }
  
  ngOnDestroy(): void {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
  }
  
  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }
  
  get currentPage(): number {
    return Math.floor(this.skip / this.limit) + 1;
  }
  
  loadProducts(): void {
    this.isLoading = true;
    this.productService.getProducts(this.skip, this.limit).subscribe({
      next: (response: any) => {
        console.log('Products loaded:', response);
        this.products = response.products || [];
        this.total = response.total || 0;
        this.filterProducts();
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Failed to load products:', err);
        this.products = [];
        this.filteredProducts = [];
        this.isLoading = false;
      }
    });
  }
  
  filterProducts(): void {
    let filtered = [...this.products];
    
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(p => 
        (p.name || '').toLowerCase().includes(term) || 
        (p.idea || '').toLowerCase().includes(term)
      );
    }
    
    if (this.statusFilter) {
      filtered = filtered.filter(p => p.status === this.statusFilter);
    }
    
    this.filteredProducts = filtered;
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
  
  getCountByStatus(status: string): number {
    return this.products.filter(p => p.status === status).length;
  }
  
  getProductEmoji(text: string): string {
    const t = (text || '').toLowerCase();
    if (t.includes('ecomm') || t.includes('shop') || t.includes('store')) return '🛒';
    if (t.includes('health') || t.includes('med') || t.includes('fitness')) return '🏥';
    if (t.includes('finance') || t.includes('payment') || t.includes('invoice')) return '💰';
    if (t.includes('social') || t.includes('chat') || t.includes('message')) return '💬';
    if (t.includes('analyt') || t.includes('dashboard')) return '📊';
    if (t.includes('ai') || t.includes('ml') || t.includes('model')) return '🤖';
    if (t.includes('game')) return '🎮';
    if (t.includes('edu') || t.includes('learn') || t.includes('school')) return '🎓';
    return '⚡';
  }
  
  formatDate(date: Date): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
  
  truncate(text: string, length: number): string {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '…' : text;
  }
  
  viewProduct(id: string): void {
    console.log('Navigating to product detail:', id);
    // Use navigateByUrl for more reliable navigation
    this.router.navigateByUrl(`/products/${id}`).then(success => {
      console.log('Navigation result:', success);
      if (!success) {
        console.error('Navigation failed');
      }
    }).catch(err => {
      console.error('Navigation error:', err);
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
}
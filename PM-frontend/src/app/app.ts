// app.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd, RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { filter, Subscription } from 'rxjs';
import { ProductService } from './services/product';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit, OnDestroy {
  currentRoute = 'Generate';
  productCount = 0;
  apiOnline = false;
  mockMode = false;
  apiUrl = '';
  apiPrefix = '';
  settingsOpen = false;
  apiDocsOpen = false;
  toastMessage = '';
  toastType = '';
  private toastTimeout: any;
  private routerSubscription: Subscription = new Subscription();
  private productSubscription: Subscription = new Subscription();

  settings = {
    baseUrl: 'http://localhost:8000',
    prefix: '/api/v1',
    token: '',
    mock: false
  };

  endpoints = [
    { method: 'POST', path: '/products/generate', desc: 'Generate complete product documentation from idea (blocking)', body: '{ "idea": "string", "product_id": "uuid (optional)" }', response: 'ProductGenerateResponse' },
    { method: 'GET', path: '/products/generate-stream', desc: 'Generate product with real-time SSE streaming updates', params: 'idea=string&product_id=uuid', response: 'text/event-stream → SSE events' },
    { method: 'GET', path: '/products/{product_id}', desc: 'Get product by UUID', params: 'product_id: UUID', response: 'ProductAPIResponse' },
    { method: 'GET', path: '/products/', desc: 'List all products with pagination', params: 'skip=0&limit=100', response: 'ProductListResponse' }
  ];

  sseEvents = [
    { type: 'start', desc: 'Pipeline started' },
    { type: 'product_created', desc: 'Product saved to DB, product_id returned' },
    { type: 'agent_start', desc: 'Agent began processing', fields: 'agent, message' },
    { type: 'agent_complete', desc: 'Agent finished, output available', fields: 'agent, output, message' },
    { type: 'outputs_update', desc: 'All current outputs snapshot', fields: 'outputs: {strategist, market_research, ...}' },
    { type: 'generating_final', desc: 'Starting final PRD generation' },
    { type: 'prd_chunk', desc: 'Word-by-word PRD token', fields: 'chunk: string' },
    { type: 'prd_complete', desc: 'Final PRD document finished' },
    { type: 'complete', desc: 'Full pipeline complete', fields: 'product_id, outputs' },
    { type: 'error', desc: 'Pipeline error', fields: 'error: string' }
  ];

  constructor(private router: Router, private productService: ProductService) {
    this.loadSettings();
    this.routerSubscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      const path = event.urlAfterRedirects;
      if (path.includes('/generate')) this.currentRoute = 'Generate';
      else if (path.includes('/products')) this.currentRoute = 'Products';
      else this.currentRoute = 'ProductForge';
    });
  }

  ngOnInit() {
    this.updateApiDisplay();
    this.checkApiStatus();
    this.loadProductCount();
    // Refresh product count periodically
    this.productSubscription = this.productService.getProducts(0, 1).subscribe({
      next: (res) => this.productCount = res.total,
      error: () => this.productCount = 0
    });
  }

  ngOnDestroy() {
    if (this.routerSubscription) {
      this.routerSubscription.unsubscribe();
    }
    if (this.productSubscription) {
      this.productSubscription.unsubscribe();
    }
    if (this.toastTimeout) clearTimeout(this.toastTimeout);
  }

  loadSettings() {
    const saved = localStorage.getItem('pf_settings');
    if (saved) {
      try {
        const s = JSON.parse(saved);
        this.settings = { ...this.settings, ...s };
      } catch(e) {}
    }
    this.mockMode = this.settings.mock;
    this.apiPrefix = this.settings.prefix;
    this.apiUrl = this.settings.baseUrl + this.settings.prefix;
  }

  saveSettings() {
    localStorage.setItem('pf_settings', JSON.stringify(this.settings));
    this.mockMode = this.settings.mock;
    this.apiPrefix = this.settings.prefix;
    this.apiUrl = this.settings.baseUrl + this.settings.prefix;
    this.checkApiStatus();
    this.showToast('Settings saved!', 'success');
    this.closeModals();
  }

  updateApiDisplay() {
    this.apiUrl = this.settings.baseUrl + this.settings.prefix;
  }

  async checkApiStatus() {
    if (this.settings.mock) {
      this.apiOnline = false;
      return;
    }
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const response = await fetch(this.settings.baseUrl + '/health', { signal: controller.signal });
      clearTimeout(timeoutId);
      this.apiOnline = response.ok;
    } catch {
      this.apiOnline = false;
    }
  }

  loadProductCount() {
    this.productService.getProducts(0, 1).subscribe({
      next: (res) => this.productCount = res.total,
      error: () => this.productCount = 0
    });
  }

  toggleSettings() {
    this.settingsOpen = !this.settingsOpen;
    if (this.settingsOpen) this.apiDocsOpen = false;
  }

  toggleApiDocs() {
    this.apiDocsOpen = !this.apiDocsOpen;
    if (this.apiDocsOpen) this.settingsOpen = false;
  }

  closeModals() {
    this.settingsOpen = false;
    this.apiDocsOpen = false;
  }

  showToast(message: string, type: string = 'default') {
    this.toastMessage = message;
    this.toastType = type;
    if (this.toastTimeout) clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => {
      this.toastMessage = '';
      this.toastType = '';
    }, 3000);
  }

  methodColor(method: string): string {
    const colors: any = { GET: '#00ff88', POST: '#4d9fff', DELETE: '#ff4d6a', PUT: '#ffaa00' };
    return colors[method] || '#c8d0e8';
  }
}
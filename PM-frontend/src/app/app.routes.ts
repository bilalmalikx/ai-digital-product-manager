// app.routes.ts
import { Routes } from '@angular/router';
import { ProductListComponent } from './components/product-list/product-list';
import { ProductGenerateComponent } from './components/product-generate/product-generate';
import { ProductDetailComponent } from './components/product-detail/product-detail';

export const routes: Routes = [
  { path: '', redirectTo: '/generate', pathMatch: 'full' },
  { path: 'generate', component: ProductGenerateComponent },
  { path: 'products', component: ProductListComponent },
  { path: 'products/:id', component: ProductDetailComponent },  // ✅ Add this route
  { path: '**', redirectTo: '/generate' }
];
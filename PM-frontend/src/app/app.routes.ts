import { Routes } from '@angular/router';
import { ProductGenerate } from './components/product-generate/product-generate';
import { ProductList } from './components/product-list/product-list';
import { ProductDetail } from './components/product-detail/product-detail';

export const routes: Routes = [
  { path: '', redirectTo: '/generate', pathMatch: 'full' },
  { path: 'generate', component: ProductGenerate },
  { path: 'products', component: ProductList },
  { path: 'product/:id', component: ProductDetail }
];
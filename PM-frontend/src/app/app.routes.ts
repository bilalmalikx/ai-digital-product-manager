import { Routes } from '@angular/router';
import { ProductGenerateComponent } from './components/product-generate/product-generate';
import { ProductListComponent } from './components/product-list/product-list';
import { ProductDetailComponent } from './components/product-detail/product-detail';


export const routes: Routes = [
  { path: '', redirectTo: '/generate', pathMatch: 'full' },
  { path: 'generate', component: ProductGenerateComponent },
  { path: 'products', component: ProductListComponent },
  { path: 'product/:id', component: ProductDetailComponent }
];
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProductGenerate } from './product-generate';

describe('ProductGenerate', () => {
  let component: ProductGenerate;
  let fixture: ComponentFixture<ProductGenerate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductGenerate]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProductGenerate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

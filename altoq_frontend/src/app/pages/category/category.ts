import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { CategoryService } from '../../services/category.service';
import { Product } from '../../models/product';
import { Category } from '../../models/category';
import { ProductCard } from '../../components/product-card/product-card';
import { Observable, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-category',
  standalone: true,
  imports: [CommonModule, RouterLink, ProductCard],
  templateUrl: './category.html',
  styleUrl: './category.css'
})
export class CategoryComponent implements OnInit {
  products$: Observable<Product[]> | undefined;
  category$: Observable<Category> | undefined;
  slug: string = '';

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private categoryService: CategoryService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.slug = params.get('slug') || '';
      if (this.slug) {
        this.loadData(this.slug);
      }
    });
  }

  loadData(slug: string): void {
    this.category$ = this.categoryService.getCategoryBySlug(slug);
    this.products$ = this.productService.getProductsByCategory(slug);
  }
}

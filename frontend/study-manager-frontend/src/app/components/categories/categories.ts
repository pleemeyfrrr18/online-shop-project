import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CategoryService } from '../../services/category';

@Component({
  selector: 'app-categories',
  imports: [CommonModule, FormsModule],
  templateUrl: './categories.html',
  styleUrl: './categories.css',
})
export class Categories implements OnInit {
  categories: any[] = [];
  errorMessage = '';
  isLoading = false;

  newCategory = { name: '', description: '' };

  constructor(private categoryService: CategoryService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadCategories();
  }

  loadCategories() {
    this.isLoading = true;
    this.categoryService.getCategories().subscribe({
      next: (data) => {
        this.categories = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to load categories';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  createCategory() {
    if (!this.newCategory.name) return;
    this.categoryService.createCategory(this.newCategory).subscribe({
      next: () => {
        this.loadCategories();
        this.newCategory = { name: '', description: '' };
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to create category';
        this.cdr.detectChanges();
      }
    });
  }

  deleteCategory(id: number) {
    this.categoryService.deleteCategory(id).subscribe({
      next: () => this.loadCategories(),
      error: () => { this.errorMessage = 'Failed to delete category'; }
    });
  }
}
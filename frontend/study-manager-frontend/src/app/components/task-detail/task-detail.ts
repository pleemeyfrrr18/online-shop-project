import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TaskService } from '../../services/task';
import { CategoryService } from '../../services/category';

@Component({
  selector: 'app-task-detail',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './task-detail.html',
  styleUrl: './task-detail.css',
})
export class TaskDetail implements OnInit {
  task: any = null;
  categories: any[] = [];
  errorMessage = '';
  isLoading = false;
  isEditing = false;
  xpMessage = '';

  statusChoices = [
    { value: 'todo', label: 'To Do' },
    { value: 'doing', label: 'In Progress' },
    { value: 'done', label: 'Done' },
  ];

  editTask = { title: '', description: '', deadline: '', status: 'todo', priority: false, category: null };

  constructor(
    private taskService: TaskService,
    private categoryService: CategoryService,
    private route: ActivatedRoute,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadTask(+id);
      this.loadCategories();
    }
  }

  loadCategories() {
    this.categoryService.getCategories().subscribe({
      next: (data) => {
        this.categories = data;
      },
      error: () => {
        this.errorMessage = 'Failed to load categories';
      }
    });
  }

  loadTask(id: number) {
    this.isLoading = true;
    this.taskService.getTask(id).subscribe({
      next: (data) => {
        this.task = data;
        this.editTask = {
          title: data.title,
          description: data.description,
          deadline: data.deadline,
          status: data.status,
          priority: data.priority,
          category: data.category || null,
        };
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to load task';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  saveTask() {
    this.taskService.updateTask(this.task.id, this.editTask).subscribe({
      next: (data) => {
        this.task = data;
        this.isEditing = false;
        this.cdr.detectChanges();
      },
      error: () => { this.errorMessage = 'Failed to update task'; }
    });
  }

  changeStatus(status: string) {
    const wasDone = this.task?.status === 'done';
    this.taskService.updateTask(this.task.id, { status }).subscribe({
      next: (data) => {
        this.task = data;
        if (!wasDone && status === 'done') {
          this.showXpMessage('+10 XP');
        }
        this.cdr.detectChanges();
      },
      error: () => { this.errorMessage = 'Failed to update status'; }
    });
  }

  finishTask() {
    this.changeStatus('done');
  }

  showXpMessage(message: string) {
    this.xpMessage = message;
    setTimeout(() => {
      this.xpMessage = '';
      this.cdr.detectChanges();
    }, 5000);
  }

  deleteTask() {
    this.taskService.deleteTask(this.task.id).subscribe({
      next: () => this.router.navigate(['/tasks']),
      error: () => { this.errorMessage = 'Failed to delete task'; }
    });
  }
}

import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TaskService } from '../../services/task';
import { CategoryService } from '../../services/category';

@Component({
  selector: 'app-task-list',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList implements OnInit {
  tasks: any[] = [];
  categories: any[] = [];
  xpMessages: Record<number, string> = {};
  errorMessage = '';
  isLoading = false;

  newTask = {
    title: '',
    description: '',
    deadline: '',
    priority: false,
    category: null,
  };

  constructor(
    private taskService: TaskService,
    private categoryService: CategoryService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadTasks();
    this.loadCategories();
  }

  loadTasks() {
    this.isLoading = true;
    this.taskService.getTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.errorMessage = 'Failed to load tasks';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
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

  createTask() {
    if (!this.newTask.title) return;
    this.taskService.createTask(this.newTask).subscribe({
      next: () => {
        this.loadTasks();
        this.newTask = { title: '', description: '', deadline: '', priority: false, category: null };
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to create task';
        this.cdr.detectChanges();
      }
    });
  }

  deleteTask(id: number) {
    this.taskService.deleteTask(id).subscribe({
      next: () => this.loadTasks(),
      error: () => { this.errorMessage = 'Failed to delete task'; }
    });
  }

  finishTask(task: any) {
    this.taskService.updateTask(task.id, { status: 'done' }).subscribe({
      next: (updatedTask: any) => {
        this.tasks = this.tasks.map((item) => item.id === task.id ? updatedTask : item);
        this.showXpMessage(task.id, '+10 XP');
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to finish task';
        this.cdr.detectChanges();
      }
    });
  }

  showXpMessage(taskId: number, message: string) {
    this.xpMessages[taskId] = message;
    setTimeout(() => {
      delete this.xpMessages[taskId];
      this.cdr.detectChanges();
    }, 5000);
  }
}

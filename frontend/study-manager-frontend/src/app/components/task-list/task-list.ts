import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TaskService } from '../../services/task';

@Component({
  selector: 'app-task-list',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './task-list.html',
  styleUrl: './task-list.css',
})
export class TaskList implements OnInit {
  tasks: any[] = [];
  errorMessage = '';
  isLoading = false;

  newTask = {
    title: '',
    description: '',
    due_date: '',
    category: null
  };

  constructor(private taskService: TaskService) {}

  ngOnInit() {
    this.loadTasks();
  }

  loadTasks() {
    this.isLoading = true;
    this.taskService.getTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Failed to load tasks';
        this.isLoading = false;
      }
    });
  }

  createTask() {
    if (!this.newTask.title) return;
    this.taskService.createTask(this.newTask).subscribe({
      next: () => {
        this.loadTasks();
        this.newTask = { title: '', description: '', due_date: '', category: null };
      },
      error: () => {
        this.errorMessage = 'Failed to create task';
      }
    });
  }

  deleteTask(id: number) {
    this.taskService.deleteTask(id).subscribe({
      next: () => this.loadTasks(),
      error: () => { this.errorMessage = 'Failed to delete task'; }
    });
  }
}
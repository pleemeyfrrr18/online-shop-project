import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { TaskService } from '../../services/task';

@Component({
  selector: 'app-task-detail',
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './task-detail.html',
  styleUrl: './task-detail.css',
})
export class TaskDetail implements OnInit {
  task: any = null;
  errorMessage = '';
  isLoading = false;
  isEditing = false;

  editTask = { title: '', description: '', due_date: '' };

  constructor(
    private taskService: TaskService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.loadTask(+id);
  }

  loadTask(id: number) {
    this.isLoading = true;
    this.taskService.getTask(id).subscribe({
      next: (data) => {
        this.task = data;
        this.editTask = { title: data.title, description: data.description, due_date: data.due_date };
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to load task';
        this.isLoading = false;
      }
    });
  }

  saveTask() {
    this.taskService.updateTask(this.task.id, this.editTask).subscribe({
      next: (data) => {
        this.task = data;
        this.isEditing = false;
      },
      error: () => { this.errorMessage = 'Failed to update task'; }
    });
  }

  deleteTask() {
    this.taskService.deleteTask(this.task.id).subscribe({
      next: () => this.router.navigate(['/tasks']),
      error: () => { this.errorMessage = 'Failed to delete task'; }
    });
  }
}
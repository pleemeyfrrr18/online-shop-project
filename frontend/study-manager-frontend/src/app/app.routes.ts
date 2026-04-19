import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { TaskList } from './components/task-list/task-list';
import { TaskDetail } from './components/task-detail/task-detail';
import { Categories } from './components/categories/categories';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'tasks', component: TaskList },
  { path: 'tasks/:id', component: TaskDetail },
  { path: 'categories', component: Categories },
  { path: '', redirectTo: '/tasks', pathMatch: 'full' },
  { path: '**', redirectTo: '/tasks' }
];
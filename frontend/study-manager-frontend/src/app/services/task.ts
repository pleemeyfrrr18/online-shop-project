import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class TaskService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  getTasks(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/tasks/`);
  }

  getTask(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/tasks/${id}/`);
  }

  createTask(task: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/tasks/`, task);
  }

  updateTask(id: number, task: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/tasks/${id}/`, task);
  }

  deleteTask(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/tasks/${id}/`);
  }
}

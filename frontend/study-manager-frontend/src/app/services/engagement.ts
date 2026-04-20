import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EngagementService {
  private apiUrl = 'http://localhost:8000/api/engagement';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  getOverview(): Observable<any> {
    return this.http.get(`${this.apiUrl}/overview/`, {
      headers: this.getHeaders()
    });
  }

  getBadges(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/badges/`, {
      headers: this.getHeaders()
    });
  }

  getActivityFeed(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/feed/`, {
      headers: this.getHeaders()
    });
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class EngagementService {
  private apiUrl = 'http://localhost:8000/api/engagement';

  constructor(private http: HttpClient) {}

  getOverview(): Observable<any> {
    return this.http.get(`${this.apiUrl}/`);
  }

  getBadges(): Observable<any> {
    return this.http.get(`${this.apiUrl}/badges/`);
  }

  getActivity(): Observable<any> {
    return this.http.get(`${this.apiUrl}/activity/`);
  }

  getSuggestions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/suggestions/`);
  }
}

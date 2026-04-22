import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface LoginCredentials {
  username: string;
  password: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/users';
  private tokenKey = 'access_token';

  constructor(private http: HttpClient) {}

  login(credentials: LoginCredentials): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, credentials)
      .pipe(
        tap((response: any) => {
          const token = response.access || response.token;
          if (token) {
            localStorage.setItem(this.tokenKey, token);
          }
        })
      );
  }

  register(credentials: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register/`, credentials);
  }

  getProfile(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me/`);
  }

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/users/`);
  }

  getFriends(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/friends/`);
  }

  getFriendRequests(): Observable<any> {
    return this.http.get(`${this.apiUrl}/friend-requests/`);
  }

  sendFriendRequest(toUserId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/friend-requests/`, { to_user: toUserId });
  }

  respondToFriendRequest(requestId: number, action: 'accept' | 'decline'): Observable<any> {
    return this.http.post(`${this.apiUrl}/friend-requests/${requestId}/action/`, { action });
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}

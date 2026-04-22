import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class TeamService {
  private apiUrl = 'http://localhost:8000/api/teams';

  constructor(private http: HttpClient) {}

  getTeams(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/`);
  }

  createTeam(team: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/`, team);
  }

  getTeam(teamId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${teamId}/`);
  }

  deleteTeam(teamId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${teamId}/`);
  }

  getTeamMembers(teamId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${teamId}/members/`);
  }

  addTeamMember(teamId: number, member: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/${teamId}/members/`, member);
  }

  getProjects(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/projects/`);
  }

  createProject(project: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/projects/`, project);
  }

  getProject(projectId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/projects/${projectId}/`);
  }

  deleteProject(projectId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/projects/${projectId}/`);
  }

  getProjectTasks(projectId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/projects/${projectId}/tasks/`);
  }

  createProjectTask(projectId: number, task: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/projects/${projectId}/tasks/`, task);
  }

  updateProjectTask(taskId: number, task: any): Observable<any> {
    return this.http.patch(`${this.apiUrl}/project-tasks/${taskId}/`, task);
  }

  deleteProjectTask(taskId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/project-tasks/${taskId}/`);
  }

  sendInvitation(invitation: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/invitations/`, invitation);
  }

  getSentInvitations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/invitations/`);
  }

  getReceivedInvitations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/received-invitations/`);
  }

  respondToInvitation(invitationId: number, action: 'accept' | 'decline'): Observable<any> {
    return this.http.post(`${this.apiUrl}/invitations/${invitationId}/action/`, { action });
  }
}

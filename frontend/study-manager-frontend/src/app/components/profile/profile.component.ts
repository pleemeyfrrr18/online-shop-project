import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { TaskService } from '../../services/task';
import { TeamService } from '../../services/team.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.css',
})
export class Profile implements OnInit {
  user: any = null;
  isLoading = true;
  errorMessage = '';
  taskCount = 0;
  teamCount = 0;
  projectCount = 0;
  activeTab: string = 'overview'; // 'overview', 'teams', 'projects', 'tasks'

  // Dashboard data
  userTeams: any[] = [];
  userProjects: any[] = [];
  userTasks: any[] = [];
  recentActivity: any[] = [];

  constructor(
    private authService: AuthService,
    private taskService: TaskService,
    private teamService: TeamService,
    private cdr: ChangeDetectorRef,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadAllData();
  }

  loadAllData() {
    this.isLoading = true;
    this.errorMessage = '';

    // Load all data in parallel
    Promise.all([
      this.loadProfilePromise(),
      this.loadCountsPromise(),
      this.loadDashboardDataPromise()
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load profile data.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadProfilePromise(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.authService.getProfile().subscribe({
        next: (data) => {
          this.user = data;
          resolve();
        },
        error: () => reject()
      });
    });
  }

  loadCountsPromise(): Promise<void> {
    return new Promise((resolve) => {
      const promises = [
        new Promise<void>((res) => {
          this.taskService.getTasks().subscribe({
            next: (tasks: any[]) => {
              this.taskCount = tasks.length;
              res();
            },
            error: () => res()
          });
        }),
        new Promise<void>((res) => {
          this.teamService.getTeams().subscribe({
            next: (teams: any[]) => {
              this.teamCount = teams.length;
              res();
            },
            error: () => res()
          });
        }),
        new Promise<void>((res) => {
          this.teamService.getProjects().subscribe({
            next: (projects: any[]) => {
              this.projectCount = projects.length;
              res();
            },
            error: () => res()
          });
        })
      ];

      Promise.all(promises).then(() => resolve());
    });
  }

  loadDashboardDataPromise(): Promise<void> {
    return new Promise((resolve) => {
      const promises = [];
      
      // Load user's teams
      promises.push(
        new Promise<void>((res) => {
          this.teamService.getTeams().subscribe({
            next: (teams: any[]) => {
              this.userTeams = teams;
              res();
            },
            error: () => res()
          });
        })
      );

      // Load user's projects
      promises.push(
        new Promise<void>((res) => {
          this.teamService.getProjects().subscribe({
            next: (projects: any[]) => {
              this.userProjects = projects;
              res();
            },
            error: () => res()
          });
        })
      );

      // Load user's tasks
      promises.push(
        new Promise<void>((res) => {
          this.taskService.getTasks().subscribe({
            next: (tasks: any[]) => {
              this.userTasks = tasks;
              res();
            },
            error: () => res()
          });
        })
      );

      Promise.all(promises).then(() => resolve());
    });
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
    this.cdr.detectChanges();
  }

  navigateToTeams() {
    this.router.navigate(['/teams']);
  }

  navigateToProjects() {
    this.router.navigate(['/projects']);
  }

  navigateToTasks() {
    this.router.navigate(['/tasks']);
  }
}

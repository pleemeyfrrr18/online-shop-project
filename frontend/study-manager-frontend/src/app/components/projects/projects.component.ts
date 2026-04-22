import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TeamService } from '../../services/team.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './projects.component.html',
  styleUrl: './projects.component.css',
})
export class Projects implements OnInit {
  projects: any[] = [];
  teams: any[] = [];
  friends: any[] = [];
  projectTasks: Record<number, any[]> = {};
  taskForms: Record<number, any> = {};
  selectedFriendByProject: Record<number, string> = {};
  xpMessages: Record<number, string> = {};
  currentUser: any = null;
  errorMessage = ''; 
  successMessage = '';
  isLoading = false;
  newProject = { title: '', description: '', deadline: '', team: null };
  newProjectTask = { project: null, title: '', description: '', priority_points: 100 };

  constructor(
    private teamService: TeamService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
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
      this.loadProjectsPromise(),
      this.loadTeamsPromise(),
      this.loadFriendsPromise()
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load projects data.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadProjectsPromise(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.teamService.getProjects().subscribe({
        next: (data) => {
          this.projects = data;
          this.projects.forEach((project) => {
            if (!this.taskForms[project.id]) {
              this.taskForms[project.id] = { title: '', description: '', priority_points: 100 };
            }
          });
          this.loadAllProjectTasks().then(() => this.cdr.detectChanges());
          resolve();
        },
        error: () => reject()
      });
    });
  }

  loadProfilePromise(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getProfile().subscribe({
        next: (data) => {
          this.currentUser = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadFriendsPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getFriends().subscribe({
        next: (data: any[]) => {
          this.friends = data.map((friendship) => friendship.friend);
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadAllProjectTasks(): Promise<void> {
    return Promise.all(this.projects.map((project) => this.loadProjectTasks(project.id))).then(() => undefined);
  }

  loadProjectTasks(projectId: number): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getProjectTasks(projectId).subscribe({
        next: (tasks) => {
          this.projectTasks[projectId] = tasks;
          resolve();
        },
        error: () => {
          this.projectTasks[projectId] = [];
          resolve();
        }
      });
    });
  }

  loadTeamsPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getTeams().subscribe({
        next: (data) => {
          this.teams = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  createProject() {
    if (!this.newProject.title || !this.newProject.team) return;
    this.teamService.createProject(this.newProject).subscribe({
      next: () => {
        this.loadProjectsPromise().then(() => this.cdr.detectChanges());
        this.newProject = { title: '', description: '', deadline: '', team: null };
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to create project.';
        this.cdr.detectChanges();
      }
    });
  }

  createTask(project: any) {
    const form = this.taskForms[project.id];
    if (!form?.title) return;

    this.teamService.createProjectTask(project.id, {
      title: form.title,
      description: form.description || '',
      priority_points: Number(form.priority_points) || 0
    }).subscribe({
      next: () => {
        this.taskForms[project.id] = { title: '', description: '', priority_points: 100 };
        Promise.all([this.loadProjectTasks(project.id), this.loadProjectsPromise()]).then(() => this.cdr.detectChanges());
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to create project task.');
        this.cdr.detectChanges();
      }
    });
  }

  createSelectedProjectTask() {
    if (!this.newProjectTask.project || !this.newProjectTask.title) return;

    const projectId = Number(this.newProjectTask.project);
    this.teamService.createProjectTask(projectId, {
      title: this.newProjectTask.title,
      description: this.newProjectTask.description || '',
      priority_points: Number(this.newProjectTask.priority_points) || 0
    }).subscribe({
      next: () => {
        this.newProjectTask = { project: null, title: '', description: '', priority_points: 100 };
        Promise.all([this.loadProjectTasks(projectId), this.loadProjectsPromise()]).then(() => this.cdr.detectChanges());
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to create project task.');
        this.cdr.detectChanges();
      }
    });
  }

  markTaskDone(project: any, task: any) {
    this.teamService.updateProjectTask(task.id, { status: 'done' }).subscribe({
      next: () => {
        this.showXpMessage(task.id, `+${task.priority_points} XP`);
        Promise.all([this.loadProjectTasks(project.id), this.loadProjectsPromise()]).then(() => this.cdr.detectChanges());
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to finish project task.');
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

  deleteProject(project: any) {
    this.teamService.deleteProject(project.id).subscribe({
      next: () => {
        this.projects = this.projects.filter((item) => item.id !== project.id);
        delete this.projectTasks[project.id];
        this.successMessage = 'Project deleted.';
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to delete project.');
        this.cdr.detectChanges();
      }
    });
  }

  sendProjectInvite(project: any) {
    const friendId = Number(this.selectedFriendByProject[project.id]);
    if (!friendId) return;

    this.teamService.sendInvitation({
      invitee: friendId,
      project: project.id,
      message: `You're invited to join ${project.title}.`
    }).subscribe({
      next: () => {
        this.selectedFriendByProject[project.id] = '';
        this.successMessage = 'Project invitation sent.';
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to send project invitation.');
        this.cdr.detectChanges();
      }
    });
  }

  isProjectOwner(project: any): boolean {
    return this.currentUser && Number(project.created_by) === Number(this.currentUser.id);
  }

  getTasks(project: any): any[] {
    return this.projectTasks[project.id] || [];
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;
    const candidate = data?.detail || data?.title || data?.priority_points || data?.non_field_errors;
    if (Array.isArray(candidate)) return candidate[0] || fallback;
    return candidate || fallback;
  }
}

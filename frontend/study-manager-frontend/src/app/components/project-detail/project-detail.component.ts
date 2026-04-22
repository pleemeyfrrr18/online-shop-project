import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { TeamService } from '../../services/team.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './project-detail.component.html',
  styleUrl: './project-detail.component.css',
})
export class ProjectDetail implements OnInit {
  project: any = null;
  tasks: any[] = [];
  friends: any[] = [];
  members: any[] = [];
  sentInvitations: any[] = [];
  currentUser: any = null;
  xpMessages: Record<number, string> = {};
  errorMessage = '';
  successMessage = '';
  inviteError = '';
  isLoading = true;
  sendingInviteUserId: number | null = null;
  newTask = { title: '', description: '', deadline: '', assigned_user: null, priority_points: 100 };

  constructor(
    private teamService: TeamService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const projectId = this.route.snapshot.paramMap.get('id');
    console.log('Project ID from route:', projectId);
    if (projectId) {
      this.loadData(+projectId);
    } else {
      this.errorMessage = 'No project ID provided.';
      this.isLoading = false;
    }
  }

  loadData(projectId: number) {
    this.isLoading = true;
    this.errorMessage = '';

    // Load all data in parallel
    Promise.all([
      this.loadProfilePromise(),
      this.loadFriendsPromise(),
      this.loadSentInvitationsPromise(),
      this.loadProjectPromise(projectId),
      this.loadTasksPromise(projectId)
    ]).then(() => {
      if (this.project?.team) {
        this.loadMembersPromise(this.project.team).then(() => this.cdr.detectChanges());
      }
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load project data.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadProfilePromise(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getProfile().subscribe({
        next: (data) => {
          this.currentUser = data;
          resolve();
        },
        error: () => {
          this.currentUser = null;
          resolve();
        }
      });
    });
  }

  loadFriendsPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getFriends().subscribe({
        next: (data) => {
          this.friends = data.map((friendship) => friendship.friend);
          resolve();
        },
        error: () => {
          this.friends = [];
          resolve();
        }
      });
    });
  }

  loadSentInvitationsPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getSentInvitations().subscribe({
        next: (data) => {
          this.sentInvitations = data;
          resolve();
        },
        error: () => {
          this.sentInvitations = [];
          resolve();
        }
      });
    });
  }

  loadProjectPromise(projectId: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.teamService.getProject(projectId).subscribe({
        next: (data) => {
          console.log('Project loaded:', data);
          this.project = data;
          resolve();
        },
        error: (err) => {
          console.error('Failed to load project:', err);
          reject();
        }
      });
    });
  }

  loadMembersPromise(teamId: number): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getTeamMembers(teamId).subscribe({
        next: (data) => {
          this.members = data;
          resolve();
        },
        error: () => {
          this.members = [];
          resolve();
        }
      });
    });
  }

  loadTasksPromise(projectId: number): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getProjectTasks(projectId).subscribe({
        next: (data) => {
          console.log('Tasks loaded:', data);
          this.tasks = data;
          resolve();
        },
        error: (err) => {
          console.error('Failed to load tasks:', err);
          this.tasks = [];
          resolve();
        }
      });
    });
  }

  createTask() {
    if (!this.project || !this.newTask.title) return;
    this.teamService.createProjectTask(this.project.id, this.newTask).subscribe({
      next: () => {
        this.loadTasksPromise(this.project.id).then(() => this.cdr.detectChanges());
        this.newTask = { title: '', description: '', deadline: '', assigned_user: null, priority_points: 100 };
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to create task:', err);
        this.errorMessage = 'Failed to create task.';
        this.cdr.detectChanges();
      }
    });
  }

  updateTaskStatus(task: any, status: string) {
    const wasDone = task.status === 'done';
    this.teamService.updateProjectTask(task.id, { status }).subscribe({
      next: () => {
        if (!wasDone && status === 'done') {
          this.showXpMessage(task.id, `+${task.priority_points} XP`);
        }
        this.loadTasksPromise(this.project.id).then(() => this.cdr.detectChanges());
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to update task:', err);
        this.errorMessage = 'Failed to update task status.';
        this.cdr.detectChanges();
      }
    });
  }

  updateTaskPriority(task: any) {
    this.teamService.updateProjectTask(task.id, { priority_points: Number(task.priority_points) || 0 }).subscribe({
      next: () => {
        this.loadData(this.project.id);
      },
      error: (err) => {
        this.errorMessage = this.getApiErrorMessage(err, 'Failed to update task priority.');
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

  deleteTask(task: any) {
    this.teamService.deleteProjectTask(task.id).subscribe({
      next: () => {
        this.loadData(this.project.id);
      },
      error: (err) => {
        this.errorMessage = this.getApiErrorMessage(err, 'Failed to delete project task.');
        this.cdr.detectChanges();
      }
    });
  }

  sendProjectInvitation(user: any) {
    if (!this.project) return;

    this.sendingInviteUserId = user.id;
    this.inviteError = '';
    this.teamService.sendInvitation({
      invitee: user.id,
      project: this.project.id,
      message: `You're invited to join ${this.project.title}.`
    }).subscribe({
      next: (invitation: any) => {
        this.sentInvitations = [invitation, ...this.sentInvitations];
        this.successMessage = `Project invitation sent to ${user.username}.`;
        this.sendingInviteUserId = null;
        this.cdr.detectChanges();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.inviteError = this.getApiErrorMessage(error, 'Failed to send project invitation.');
        this.sendingInviteUserId = null;
        this.cdr.detectChanges();
      }
    });
  }

  isTeamMember(user: any): boolean {
    return this.members.some((member) => Number(member.user) === Number(user.id));
  }

  hasPendingProjectInvite(user: any): boolean {
    if (!this.project) return false;
    return this.sentInvitations.some((invitation) => {
      return Number(invitation.invitee) === Number(user.id)
        && Number(invitation.project) === Number(this.project.id)
        && invitation.status === 'pending';
    });
  }

  inviteButtonLabel(user: any): string {
    if (this.isTeamMember(user)) return 'In Project';
    if (this.hasPendingProjectInvite(user)) return 'Invited';
    if (this.sendingInviteUserId === user.id) return 'Sending...';
    return 'Invite';
  }

  canInviteUser(user: any): boolean {
    return !this.isTeamMember(user)
      && !this.hasPendingProjectInvite(user)
      && this.sendingInviteUserId !== user.id;
  }

  getCompletedCount(): number {
    return this.tasks.filter(t => t.status === 'done').length;
  }

  getProgressPercent(): number {
    const totalPoints = this.tasks.reduce((sum, task) => sum + Number(task.priority_points || 0), 0);
    if (totalPoints === 0) return 0;
    const completedPoints = this.tasks
      .filter(task => task.status === 'done')
      .reduce((sum, task) => sum + Number(task.priority_points || 0), 0);
    return Math.round((completedPoints / totalPoints) * 100);
  }

  getCompletedPoints(): number {
    return this.tasks
      .filter(task => task.status === 'done')
      .reduce((sum, task) => sum + Number(task.priority_points || 0), 0);
  }

  isProjectOwner(): boolean {
    return this.currentUser && this.project && Number(this.project.created_by) === Number(this.currentUser.id);
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;

    if (typeof data === 'string') {
      return data;
    }

    const candidate = data?.detail || data?.project || data?.invitee || data?.non_field_errors;
    if (Array.isArray(candidate)) {
      return candidate[0] || fallback;
    }

    return candidate || fallback;
  }
}

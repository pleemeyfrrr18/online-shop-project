import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { TeamService } from '../../services/team.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-team-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './team-detail.component.html',
  styleUrl: './team-detail.component.css',
})
export class TeamDetail implements OnInit {
  team: any = null;
  members: any[] = [];
  teamProjects: any[] = [];
  currentUser: any = null;
  errorMessage = '';
  successMessage = '';
  isLoading = true;
  newMember = { user: '', role: 'member' };
  showInviteForm = false;
  isSendingInvitation = false;
  newInvite = { inviteeUsername: '', message: '' };
  inviteError = '';

  constructor(
    private teamService: TeamService,
    private route: ActivatedRoute,
    private cdr: ChangeDetectorRef,
    private authService: AuthService
  ) {}

  ngOnInit() {
    const teamId = this.route.snapshot.paramMap.get('id');
    console.log('Team ID from route:', teamId);
    if (teamId) {
      this.loadData(+teamId);
    } else {
      this.errorMessage = 'No team ID provided.';
      this.isLoading = false;
    }
  }

  loadData(teamId: number) {
    this.isLoading = true;
    this.errorMessage = '';

    // Load all data in parallel
    Promise.all([
      this.loadProfilePromise(),
      this.loadTeamPromise(teamId),
      this.loadMembersPromise(teamId),
      this.loadTeamProjectsPromise(teamId)
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load team data.';
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

  loadTeamPromise(teamId: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.teamService.getTeam(teamId).subscribe({
        next: (data) => {
          console.log('Team loaded:', data);
          this.team = data;
          resolve();
        },
        error: (err) => {
          console.error('Failed to load team:', err);
          reject();
        }
      });
    });
  }

  loadMembersPromise(teamId: number): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getTeamMembers(teamId).subscribe({
        next: (data) => {
          console.log('Members loaded:', data);
          this.members = data;
          resolve();
        },
        error: (err) => {
          console.error('Failed to load members:', err);
          this.members = [];
          resolve();
        }
      });
    });
  }

  loadTeamProjectsPromise(teamId: number): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getProjects().subscribe({
        next: (data: any[]) => {
          console.log('Projects loaded:', data);
          this.teamProjects = data.filter(p => p.team === teamId);
          resolve();
        },
        error: (err) => {
          console.error('Failed to load projects:', err);
          this.teamProjects = [];
          resolve();
        }
      });
    });
  }

  get canInviteMembers(): boolean {
    if (!this.currentUser) {
      return false;
    }

    return this.members.some((member) => {
      return Number(member.user) === Number(this.currentUser.id) && member.role === 'owner';
    });
  }

  addMember() {
    if (!this.team || !this.newMember.user) return;
    this.teamService.addTeamMember(this.team.id, this.newMember).subscribe({
      next: () => {
        this.newMember = { user: '', role: 'member' };
        this.loadMembersPromise(this.team.id).then(() => this.cdr.detectChanges());
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to add member:', err);
        this.errorMessage = 'Failed to add team member.';
        this.cdr.detectChanges();
      }
    });
  }

  sendInvitation() {
    if (!this.team) {
      return;
    }

    if (!this.canInviteMembers) {
      this.inviteError = 'Only team owners can send invitations.';
      return;
    }

    const inviteeUsername = this.newInvite.inviteeUsername.trim();
    if (!inviteeUsername) {
      this.inviteError = 'Please enter a username.';
      return;
    }

    const invitation = {
      invitee_username: inviteeUsername,
      team: this.team.id,
      message: this.newInvite.message.trim()
    };

    this.isSendingInvitation = true;
    this.inviteError = '';
    this.teamService.sendInvitation(invitation).subscribe({
      next: () => {
        this.successMessage = `Invitation sent to ${inviteeUsername}!`;
        this.newInvite = { inviteeUsername: '', message: '' };
        this.showInviteForm = false;
        this.inviteError = '';
        this.isSendingInvitation = false;
        this.cdr.detectChanges();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (err) => {
        this.inviteError = this.getApiErrorMessage(err, 'Failed to send invitation.');
        this.isSendingInvitation = false;
        this.cdr.detectChanges();
      }
    });
  }

  toggleInviteForm() {
    this.showInviteForm = !this.showInviteForm;
    this.inviteError = '';
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;

    if (typeof data === 'string') {
      return data;
    }

    const candidate = data?.detail || data?.invitee_username || data?.invitee || data?.non_field_errors;
    if (Array.isArray(candidate)) {
      return candidate[0] || fallback;
    }

    return candidate || fallback;
  }
}

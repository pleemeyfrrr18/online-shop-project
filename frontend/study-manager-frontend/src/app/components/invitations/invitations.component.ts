import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TeamService } from '../../services/team.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-invitations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './invitations.component.html',
  styleUrl: './invitations.component.css',
})
export class Invitations implements OnInit {
  friends: any[] = [];
  ownedTeams: any[] = [];
  sentInvitations: any[] = [];
  receivedInvitations: any[] = [];
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  activeTab = 'invite';
  selectedTeamId = '';
  inviteMessages: Record<number, string> = {};
  sendingInviteUserId: number | null = null;

  constructor(
    private teamService: TeamService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadInvitations();
  }

  loadInvitations() {
    this.isLoading = true;
    this.errorMessage = '';

    Promise.all([
      this.loadFriends(),
      this.loadOwnedTeams(),
      this.loadSentInvitations(),
      this.loadReceivedInvitations()
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load invitations.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadFriends(): Promise<void> {
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

  loadOwnedTeams(): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getTeams().subscribe({
        next: (teams: any[]) => {
          this.resolveOwnedTeams(teams).then(resolve);
        },
        error: () => {
          this.ownedTeams = [];
          resolve();
        }
      });
    });
  }

  resolveOwnedTeams(teams: any[]): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getProfile().subscribe({
        next: (profile: any) => {
          Promise.all(teams.map((team) => this.teamOwnerCheck(team, profile.id))).then((ownership) => {
            this.ownedTeams = ownership.filter((result) => result.isOwner).map((result) => result.team);
            if (!this.selectedTeamId && this.ownedTeams.length) {
              this.selectedTeamId = String(this.ownedTeams[0].id);
            }
            resolve();
          });
        },
        error: () => {
          this.ownedTeams = [];
          resolve();
        }
      });
    });
  }

  teamOwnerCheck(team: any, currentUserId: number): Promise<{ team: any; isOwner: boolean }> {
    return new Promise((resolve) => {
      this.teamService.getTeamMembers(team.id).subscribe({
        next: (members: any[]) => {
          const isOwner = members.some((member) => {
            return Number(member.user) === Number(currentUserId) && member.role === 'owner';
          });
          resolve({ team, isOwner });
        },
        error: () => resolve({ team, isOwner: false })
      });
    });
  }

  loadSentInvitations(): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getSentInvitations().subscribe({
        next: (data: any[]) => {
          this.sentInvitations = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadReceivedInvitations(): Promise<void> {
    return new Promise((resolve) => {
      this.teamService.getReceivedInvitations().subscribe({
        next: (data: any[]) => {
          this.receivedInvitations = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;
    this.cdr.detectChanges();
  }

  sendInvitationToUser(user: any) {
    if (!this.selectedTeamId) {
      this.errorMessage = 'Choose a team before sending an invitation.';
      return;
    }

    this.sendingInviteUserId = user.id;
    this.errorMessage = '';

    this.teamService.sendInvitation({
      invitee: user.id,
      team: Number(this.selectedTeamId),
      message: (this.inviteMessages[user.id] || '').trim()
    }).subscribe({
      next: (invitation: any) => {
        this.successMessage = `Invitation sent to ${user.username}.`;
        this.inviteMessages[user.id] = '';
        this.sentInvitations = [invitation, ...this.sentInvitations];
        this.sendingInviteUserId = null;
        this.cdr.detectChanges();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to send invitation.');
        this.sendingInviteUserId = null;
        this.cdr.detectChanges();
      }
    });
  }

  hasPendingInvite(user: any): boolean {
    if (!this.selectedTeamId) {
      return false;
    }

    return this.sentInvitations.some((invitation) => {
      return Number(invitation.invitee) === Number(user.id)
        && Number(invitation.team) === Number(this.selectedTeamId)
        && !invitation.project
        && invitation.status === 'pending';
    });
  }

  acceptInvitation(invitation: any) {
    this.teamService.respondToInvitation(invitation.id, 'accept').subscribe({
      next: () => {
        this.successMessage = 'Invitation accepted!';
        this.loadInvitations();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to accept invitation.');
      }
    });
  }

  declineInvitation(invitation: any) {
    this.teamService.respondToInvitation(invitation.id, 'decline').subscribe({
      next: () => {
        this.successMessage = 'Invitation declined.';
        this.loadInvitations();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to decline invitation.');
      }
    });
  }

  getStatusClass(status: string): string {
    return `status-${status.toLowerCase()}`;
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;

    if (typeof data === 'string') {
      return data;
    }

    const candidate = data?.detail || data?.invitee || data?.invitee_username || data?.non_field_errors;
    if (Array.isArray(candidate)) {
      return candidate[0] || fallback;
    }

    return candidate || fallback;
  }
}

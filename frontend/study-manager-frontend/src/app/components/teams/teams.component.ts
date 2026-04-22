import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { TeamService } from '../../services/team.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-teams',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './teams.component.html',
  styleUrl: './teams.component.css',
})
export class Teams implements OnInit {
  teams: any[] = [];
  friends: any[] = [];
  currentUser: any = null;
  selectedFriendByTeam: Record<number, string> = {};
  errorMessage = '';
  successMessage = '';
  isLoading = false;
  newTeam = { name: '', description: '' };

  constructor(
    private teamService: TeamService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadAllData();
  }

  loadAllData() {
    Promise.all([
      this.loadProfile(),
      this.loadFriends(),
      this.loadTeamsPromise()
    ]).then(() => this.cdr.detectChanges());
  }

  loadTeams() {
    this.isLoading = true;
    this.teamService.getTeams().subscribe({
      next: (data) => {
        this.teams = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to load teams.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  loadTeamsPromise(): Promise<void> {
    this.isLoading = true;
    return new Promise((resolve) => {
      this.teamService.getTeams().subscribe({
        next: (data) => {
          this.teams = data;
          this.isLoading = false;
          resolve();
        },
        error: () => {
          this.errorMessage = 'Failed to load teams.';
          this.isLoading = false;
          resolve();
        }
      });
    });
  }

  loadProfile(): Promise<void> {
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

  createTeam() {
    if (!this.newTeam.name) return;
    this.teamService.createTeam(this.newTeam).subscribe({
      next: () => {
        this.loadTeams();
        this.newTeam = { name: '', description: '' };
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = 'Failed to create team.';
        this.cdr.detectChanges();
      }
    });
  }

  sendTeamInvite(team: any) {
    const friendId = Number(this.selectedFriendByTeam[team.id]);
    if (!friendId) return;

    this.teamService.sendInvitation({
      invitee: friendId,
      team: team.id,
      message: `You're invited to join ${team.name}.`
    }).subscribe({
      next: () => {
        this.selectedFriendByTeam[team.id] = '';
        this.successMessage = 'Team invitation sent.';
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to send team invitation.');
        this.cdr.detectChanges();
      }
    });
  }

  deleteTeam(team: any) {
    this.teamService.deleteTeam(team.id).subscribe({
      next: () => {
        this.teams = this.teams.filter((item) => item.id !== team.id);
        this.successMessage = 'Team deleted.';
        this.cdr.detectChanges();
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to delete team.');
        this.cdr.detectChanges();
      }
    });
  }

  isTeamOwner(team: any): boolean {
    return this.currentUser && Number(team.creator) === Number(this.currentUser.id);
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;
    const candidate = data?.detail || data?.non_field_errors;
    if (Array.isArray(candidate)) return candidate[0] || fallback;
    return candidate || fallback;
  }
}

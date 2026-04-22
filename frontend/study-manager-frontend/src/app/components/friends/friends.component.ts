import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-friends',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './friends.component.html',
  styleUrl: './friends.component.css',
})
export class Friends implements OnInit {
  users: any[] = [];
  friends: any[] = [];
  receivedRequests: any[] = [];
  sentRequests: any[] = [];
  updates: any[] = [];
  activeTab = 'players';
  isLoading = true;
  sendingUserId: number | null = null;
  respondingRequestId: number | null = null;
  errorMessage = '';
  successMessage = '';

  constructor(
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.isLoading = true;
    this.errorMessage = '';

    Promise.all([
      this.loadUsers(),
      this.loadFriends(),
      this.loadFriendRequests()
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load friends.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadUsers(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getUsers().subscribe({
        next: (users) => {
          this.users = users;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadFriends(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getFriends().subscribe({
        next: (friends) => {
          this.friends = friends;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadFriendRequests(): Promise<void> {
    return new Promise((resolve) => {
      this.authService.getFriendRequests().subscribe({
        next: (data: any) => {
          this.receivedRequests = data.received || [];
          this.sentRequests = data.sent || [];
          this.updates = data.updates || [];
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

  sendRequest(user: any) {
    this.sendingUserId = user.id;
    this.errorMessage = '';

    this.authService.sendFriendRequest(user.id).subscribe({
      next: (request) => {
        this.sentRequests = [request, ...this.sentRequests];
        this.successMessage = `Friend request sent to ${user.username}.`;
        this.sendingUserId = null;
        this.cdr.detectChanges();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, 'Failed to send friend request.');
        this.sendingUserId = null;
        this.cdr.detectChanges();
      }
    });
  }

  respondToRequest(request: any, action: 'accept' | 'decline') {
    this.respondingRequestId = request.id;
    this.errorMessage = '';

    this.authService.respondToFriendRequest(request.id, action).subscribe({
      next: () => {
        this.successMessage = action === 'accept'
          ? `You are now friends with ${request.from_user_username}.`
          : `Friend request from ${request.from_user_username} declined.`;
        this.respondingRequestId = null;
        this.loadData();
        setTimeout(() => (this.successMessage = ''), 3000);
      },
      error: (error) => {
        this.errorMessage = this.getApiErrorMessage(error, `Failed to ${action} friend request.`);
        this.respondingRequestId = null;
        this.cdr.detectChanges();
      }
    });
  }

  isFriend(user: any): boolean {
    return this.friends.some((friendship) => Number(friendship.friend.id) === Number(user.id));
  }

  pendingSentRequest(user: any): any {
    return this.sentRequests.find((request) => {
      return Number(request.to_user) === Number(user.id) && request.status === 'pending';
    });
  }

  pendingReceivedRequest(user: any): any {
    return this.receivedRequests.find((request) => Number(request.from_user) === Number(user.id));
  }

  latestUpdate(user: any): any {
    return this.updates.find((request) => Number(request.to_user) === Number(user.id));
  }

  playerButtonLabel(user: any): string {
    if (this.isFriend(user)) {
      return 'Friends';
    }
    if (this.pendingSentRequest(user)) {
      return 'Pending';
    }
    if (this.pendingReceivedRequest(user)) {
      return 'Respond';
    }
    if (this.sendingUserId === user.id) {
      return 'Sending...';
    }
    const update = this.latestUpdate(user);
    if (update?.status === 'declined') {
      return 'Declined';
    }
    return 'Add Friend';
  }

  canSendRequest(user: any): boolean {
    return !this.isFriend(user)
      && !this.pendingSentRequest(user)
      && !this.pendingReceivedRequest(user)
      && this.latestUpdate(user)?.status !== 'declined'
      && this.sendingUserId !== user.id;
  }

  statusClass(status: string): string {
    return `status-${status}`;
  }

  private getApiErrorMessage(error: any, fallback: string): string {
    const data = error?.error;

    if (typeof data === 'string') {
      return data;
    }

    const candidate = data?.detail || data?.to_user || data?.to_username || data?.non_field_errors;
    if (Array.isArray(candidate)) {
      return candidate[0] || fallback;
    }

    return candidate || fallback;
  }
}

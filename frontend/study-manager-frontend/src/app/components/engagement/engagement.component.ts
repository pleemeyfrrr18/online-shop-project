import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EngagementService } from '../../services/engagement.service';

@Component({
  selector: 'app-engagement',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './engagement.component.html',
  styleUrl: './engagement.component.css',
})
export class Engagement implements OnInit {
  overview: any = null;
  badges: any[] = [];
  activity: any[] = [];
  suggestions: any[] = [];
  errorMessage = '';
  isLoading = false;

  constructor(private engagementService: EngagementService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadAllData();
  }

  loadAllData() {
    this.isLoading = true;
    this.errorMessage = '';

    // Load all data in parallel
    Promise.all([
      this.loadOverviewPromise(),
      this.loadBadgesPromise(),
      this.loadActivityPromise(),
      this.loadSuggestionsPromise()
    ]).then(() => {
      this.isLoading = false;
      this.cdr.detectChanges();
    }).catch(() => {
      this.errorMessage = 'Failed to load engagement data.';
      this.isLoading = false;
      this.cdr.detectChanges();
    });
  }

  loadOverviewPromise(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.engagementService.getOverview().subscribe({
        next: (data) => {
          this.overview = data;
          resolve();
        },
        error: () => reject()
      });
    });
  }

  loadBadgesPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.engagementService.getBadges().subscribe({
        next: (data) => {
          this.badges = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadActivityPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.engagementService.getActivity().subscribe({
        next: (data) => {
          this.activity = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }

  loadSuggestionsPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.engagementService.getSuggestions().subscribe({
        next: (data) => {
          this.suggestions = data;
          resolve();
        },
        error: () => resolve()
      });
    });
  }
}

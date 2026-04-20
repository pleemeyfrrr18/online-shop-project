import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { EngagementService } from '../../services/engagement';

@Component({
  selector: 'app-navbar',
  imports: [RouterModule, CommonModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class Navbar implements OnInit {
  xp = 0;
  level = 1;

  constructor(
    private authService: AuthService,
    private router: Router,
    private engagementService: EngagementService
  ) {}

  ngOnInit() {
    this.engagementService.getOverview().subscribe({
      next: (data) => {
        this.xp = data.profile.xp;
        this.level = data.profile.level;
      },
      error: () => {}
    });
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
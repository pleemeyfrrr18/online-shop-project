import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { AuthGuard } from './guards/auth.guard';
import { TaskList } from './components/task-list/task-list';
import { TaskDetail } from './components/task-detail/task-detail';
import { Categories } from './components/categories/categories';
import { Register } from './components/register/register.component';
import { Profile } from './components/profile/profile.component';
import { Engagement } from './components/engagement/engagement.component';
import { Teams } from './components/teams/teams.component';
import { TeamDetail } from './components/team-detail/team-detail.component';
import { Projects } from './components/projects/projects.component';
import { ProjectDetail } from './components/project-detail/project-detail.component';
import { Invitations } from './components/invitations/invitations.component';
import { Friends } from './components/friends/friends.component';
import { About } from './components/about/about.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: Register },
  { path: 'about', component: About },
  { path: 'tasks', component: TaskList, canActivate: [AuthGuard] },
  { path: 'tasks/:id', component: TaskDetail, canActivate: [AuthGuard] },
  { path: 'categories', component: Categories, canActivate: [AuthGuard] },
  { path: 'profile', component: Profile, canActivate: [AuthGuard] },
  { path: 'engagement', component: Engagement, canActivate: [AuthGuard] },
  { path: 'teams', component: Teams, canActivate: [AuthGuard] },
  { path: 'teams/:id', component: TeamDetail, canActivate: [AuthGuard] },
  { path: 'projects', component: Projects, canActivate: [AuthGuard] },
  { path: 'projects/:id', component: ProjectDetail, canActivate: [AuthGuard] },
  { path: 'invitations', component: Invitations, canActivate: [AuthGuard] },
  { path: 'friends', component: Friends, canActivate: [AuthGuard] },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: '**', redirectTo: '/login' }
];

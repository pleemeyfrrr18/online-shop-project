# Study Manager

Study Manager is a full-stack web application for organizing student work, personal tasks, team projects, invitations, and progress tracking. It combines an Angular frontend with a Django REST Framework backend and JWT authentication.

## Group Members

- Уәлихан Шоқан 24B032094
- Түркпен Адия 24B032076
- Карамурзанов Арсен 24B031049

## Project Description

The application helps students manage both individual study plans and collaborative academic projects. Users can register, log in, create personal tasks, organize tasks by categories, join teams, invite friends to projects, complete weighted project tasks, and track XP progress.

Study Manager supports two main workflows:

- Personal productivity: users create their own tasks, set deadlines, categorize work, mark tasks as finished, and earn XP.
- Collaborative project work: users become friends, create teams, invite friends to teams or projects, split a project into weighted tasks, finish project tasks, and update shared project progress.

## Main Features

- JWT authentication with login, registration, logout, protected routes, and HTTP interceptor.
- Personal task CRUD: create, view, update, delete, and finish tasks.
- Task categories for organizing assignments by subject or topic.
- Friends system: registered users can send friend requests, accept them, decline them, and see request updates.
- Team management: users can create teams, view team members, invite friends, and delete teams as the owner.
- Project management: users can create team projects, view project details, invite friends to projects, and delete owned projects.
- Project invitations: invited users see project information and can accept or decline the invitation.
- Weighted project tasks: each project task has priority points; priorities are normalized to total 100.
- Project progress: finishing a project task increases the project progress by that task's priority value.
- Project completion: when all project tasks are done, the project status changes to finished.
- XP and levels: users gain XP for creating teams/projects/tasks and completing personal or project tasks.
- Engagement dashboard: shows profile progress, XP, badges, activity feed, and smart suggestions.
- About page: clicking the Study Manager logo opens the About page with app information and a back button.
- Postman collection: committed API collection with example requests and responses.

## Technology Stack

### Frontend

- Angular
- TypeScript
- Angular Router
- FormsModule with `[(ngModel)]`
- HttpClient services
- JWT HTTP interceptor
- Component CSS styling

### Backend

- Python
- Django
- Django REST Framework
- Simple JWT
- django-cors-headers
- SQLite database for local development

## Frontend Routes

- `/login` - login page
- `/register` - registration page
- `/about` - application description page
- `/tasks` - personal task list
- `/tasks/:id` - personal task details
- `/categories` - task categories
- `/profile` - user profile, XP, teams, projects, and tasks summary
- `/engagement` - XP, badges, activity, and suggestions
- `/teams` - team list and team creation
- `/teams/:id` - team details, members, and projects
- `/projects` - project list, project creation, and project tasks
- `/projects/:id` - project details and project task list
- `/invitations` - sent and received team/project invitations
- `/friends` - users, friends, friend requests, and request updates

Opening `localhost:4200` redirects to `/login`.

## Backend API Overview

### Authentication and Users

- `POST /api/users/register/`
- `POST /api/users/login/`
- `POST /api/users/logout/`
- `GET /api/users/me/`
- `GET /api/users/users/`

### Friends

- `GET /api/users/friends/`
- `GET /api/users/friend-requests/`
- `POST /api/users/friend-requests/`
- `POST /api/users/friend-requests/<id>/action/`

### Tasks and Categories

- `GET /api/tasks/`
- `POST /api/tasks/`
- `GET /api/tasks/<id>/`
- `PATCH /api/tasks/<id>/`
- `DELETE /api/tasks/<id>/`
- `GET /api/tasks/categories/`
- `POST /api/tasks/categories/`
- `GET /api/tasks/categories/<id>/`
- `PATCH /api/tasks/categories/<id>/`
- `DELETE /api/tasks/categories/<id>/`

### Teams, Projects, Project Tasks, and Invitations

- `GET /api/teams/`
- `POST /api/teams/`
- `GET /api/teams/<id>/`
- `PATCH /api/teams/<id>/`
- `DELETE /api/teams/<id>/`
- `GET /api/teams/<id>/members/`
- `POST /api/teams/<id>/members/`
- `GET /api/teams/projects/`
- `POST /api/teams/projects/`
- `GET /api/teams/projects/<id>/`
- `PATCH /api/teams/projects/<id>/`
- `DELETE /api/teams/projects/<id>/`
- `GET /api/teams/projects/<project_id>/tasks/`
- `POST /api/teams/projects/<project_id>/tasks/`
- `PATCH /api/teams/project-tasks/<id>/`
- `DELETE /api/teams/project-tasks/<id>/`
- `GET /api/teams/invitations/`
- `POST /api/teams/invitations/`
- `GET /api/teams/received-invitations/`
- `POST /api/teams/invitations/<id>/action/`

### Engagement

- `GET /api/engagement/`
- `GET /api/engagement/profile/`
- `GET /api/engagement/badges/`
- `GET /api/engagement/activity/`
- `GET /api/engagement/suggestions/`

## Backend Models

The backend includes models for:

- `Task`
- `Category`
- `Team`
- `TeamMember`
- `Project`
- `ProjectTask`
- `Invitation`
- `JoinRequest`
- `FriendRequest`
- `Friendship`
- `UserProfile`
- `Badge`
- `UserBadge`
- `ActivityFeed`

## How To Run Locally

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend/study-manager-frontend
npm install
npm start
```

The frontend runs at:

```text
http://localhost:4200
```

## Postman Collection

The project includes a Postman collection for testing the API:

```text
postman/study-manager.postman_collection.json
```

Import it into Postman, run the login request, and the JWT access token will be saved automatically as `accessToken`. The collection includes requests for authentication, tasks, categories, friends, teams, projects, project tasks, invitations, and engagement.

More instructions are available in:

```text
postman/README.md
```

## Important Project Logic

- Personal tasks belong to the authenticated user through `request.user`.
- Categories also belong to the authenticated user.
- Teams are created by a user, and the creator automatically becomes the team owner.
- Team and project invitations can only be sent to friends.
- Accepting a team invitation adds the invited user to the team.
- Accepting a project invitation adds the invited user to the project through team membership.
- Project task priority points are automatically normalized so the total priority is exactly 100.
- Completing a project task increases project progress by the task priority amount.
- When all project tasks are done, the project becomes finished and XP is awarded based on contribution.

## Requirements Covered

### Angular

- Interfaces and services communicate with backend APIs through `HttpClient`.
- Multiple click events trigger API requests for tasks, categories, friends, teams, projects, and invitations.
- Forms use `[(ngModel)]` for login, registration, task forms, project forms, team forms, invitation forms, and project task forms.
- Angular routing includes more than three named routes.
- Templates use Angular control flow such as `@for` and `@if`.
- JWT authentication is handled with login, logout, protected routes, and an HTTP interceptor.
- API errors are displayed to users through component error messages.

### Django and DRF

- The backend defines more than four models.
- Models include multiple `ForeignKey` relationships.
- Serializers include both `serializers.Serializer` and `serializers.ModelSerializer`.
- Views include DRF function-based views and class-based API views.
- Authentication uses JWT login and protected endpoints.
- Tasks provide full CRUD operations.
- Objects are linked to the authenticated user when created.
- CORS is configured for the Angular development server.
- A Postman collection with example requests and responses is committed to the repository.


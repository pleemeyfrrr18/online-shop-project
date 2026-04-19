# Study manager

## Group members
  - Уәлихан Шоқан 24B032094
  - Түркпен Адия 24B032076
  - Карамурзанов Арсен 24B031049

## Description

Study Manager is a web application designed to help students organize and manage their academic tasks efficiently.

It allows users to create, edit, and track tasks, set deadlines, and categorize their work to improve productivity and avoid missing important assignments.

⭐ Key Features\
    - 🔐 User Authentication (JWT) — each user has a personal workspace\
    - 📝 Task Management (CRUD) — create, update, delete, and view tasks\
    - 📂 Categories — organize tasks by subjects or topics\
    - 🔍 Search & Filtering — quickly find tasks by name or status\
    - ⏱ Deadline Tracking — keep track of upcoming assignments\
    - 📊 Progress Tracking — monitor completed vs pending tasks\

You can add a Team Project feature where users can create a team with friends and work on shared academic projects together.

### What users can do
    - create a team
    - invite friends to join
    - create a group project inside the team
    - assign tasks to team members
    - track the progress of the whole group
    - see who completed which task

### Main idea

There will be:
    - personal tasks for one user
    - team projects for several users

So the app supports both individual study planning and group work.

You can add these models:

Team\
    - name\
    - description\
    - creator\
TeamMember\
    - user\
    - team\
    - role\
Project\
    - title\
    - description\
    - deadline\
    - team\
ProjectTask\
    - title\
    - status\
    - assigned_user\
    - project\
    

### 🧭 1. Application Structure (Routing)

The application uses Angular routing with the following pages:

  - /login — Login page
  - /tasks — Task list page (main dashboard)
  - /tasks/:id — Task detail page
  - /categories — Categories page

Navigation is implemented via a top navbar.


### 🔐 2. Login Page (/login)
💡 Purpose:

Allows users to authenticate using JWT.

⚙️ Features:
  - Login form:
  - username
  - password
  - Two-way binding using [(ngModel)]
  - Submit button → (click) event → API request
  - Error handling (invalid credentials message)
    
🔗 Backend:
  - POST /api/login/
  - Returns JWT token
  - 
✅ Covers:
  - FormsModule ✔️
  - click event ✔️
  - error handling ✔️

  
### 📋 3. Task List Page (/tasks)
💡 Purpose:

Main dashboard displaying all user tasks.

⚙️ Features:
  - Display tasks using @for
  - Conditional UI using @if (e.g., “No tasks yet”)
  - Each task card shows:
  - title
  - deadline
  - status
  - priority
  
🎯 Actions:
  - ➕ Add task button (click)
  - ❌ Delete task (click)
  - ⭐ Mark as important (click)
  - 🔍 Search input with [(ngModel)]
  - 📂 Filter by category

🔗 Backend:
  - GET /api/tasks/
  - DELETE /api/tasks/:id/
  
✅ Covers:
  - ≥4 click events ✔️
  - ngModel ✔️
  - @for / @if ✔️
  
### 📄 4. Task Detail Page (/tasks/:id)
💡 Purpose:

View and edit a specific task.

⚙️ Features:
Display full task info:
  - title
  - description
  - deadline
  - category
  - Edit form using [(ngModel)]
  - Update button (click)
  - Delete button (click)
  
🔗 Backend:
  - GET /api/tasks/:id/
  - PUT /api/tasks/:id/
  - DELETE /api/tasks/:id/
  
✅ Covers:
  - CRUD ✔️
  - Forms ✔️
  - click events ✔️

  
### ➕ 5. Create Task (Modal or Section)
💡 Purpose:

Create new tasks.

⚙️ Features:

Form fields:
  - title
  - description
  - deadline
  - category
  - Submit (click) → POST request
    
🔗 Backend:
POST /api/tasks/
Automatically links task to request.user

✅ Covers:
CRUD ✔️
Forms ✔️


### 📂 6. Categories Page (/categories)
💡 Purpose:

Manage task categories.

⚙️ Features:
  - List categories (@for)
  - Add category (click)
  - Delete category (click)
  - Filter tasks by category
  - 
🔗 Backend:
  - GET /api/categories/
  - POST /api/categories/
  - DELETE /api/categories/:id/
  - 
✅ Covers:
ForeignKey usage ✔️
CRUD ✔️


### 👤 7. User + Authentication Logic
⚙️ Features:
  - JWT stored in localStorage
  - HTTP Interceptor adds token to requests
  - Logout button (click) clears token
  - Protected routes (only logged-in users can access tasks)
    
🔗 Backend:
Token-based authentication

✅ Covers:
  - JWT ✔️
  - interceptor ✔️
    
⚙️ Backend Structure (Django + DRF)

📦 Models:
  - User
  - Task
  - Category
  - Comment (optional)

🔗 Relationships:
  - Task → User (ForeignKey)
  - Task → Category (ForeignKey)
  
🔄 Serializers:
  - TaskSerializer (ModelSerializer)
  - CategorySerializer (ModelSerializer)
  - LoginSerializer (Serializer)
  - RegisterSerializer (Serializer)
  
🌐 Views:
  - FBV:
  - login
  - logout
  - CBV:
  - TaskListCreateAPIView
  - TaskDetailAPIView

# Study Manager Postman Collection

This folder contains an importable Postman collection for the Django REST API:

- `study-manager.postman_collection.json`

## How to Import the Collection

1. Open Postman.
2. Click **Import** in the top-left corner.
3. Choose **Files**.
4. Select `postman/study-manager.postman_collection.json`.
5. Click **Import**.
6. Open the imported collection named **Study Manager API**.

## How to Run Requests

1. Start the Django backend server:

   ```bash
   python manage.py runserver
   ```

2. In Postman, open the collection variables and check `baseUrl`.
   The default value is:

   ```text
   http://127.0.0.1:8000
   ```

3. Run **Auth / Register User** if you need a new test account.
4. Run **Auth / Login User**.
   This request automatically saves the JWT values into collection variables:

   - `accessToken`
   - `refreshToken`

5. After login, run protected requests like:

   - **Tasks and Categories / Create Task**
   - **Friends / Send Friend Request**
   - **Teams, Projects, Project Tasks, Invitations / Create Team**
   - **Engagement / Engagement Overview**

6. Some requests save IDs automatically after creation:

   - `categoryId`
   - `taskId`
   - `teamId`
   - `projectId`
   - `projectTaskId`
   - `invitationId`
   - `friendRequestId`

7. For friend and invitation flows, use two users:

   - Login as user 1 and send a friend request or invitation.
   - Login as user 2 and accept or decline it.
   - Postman updates `accessToken` every time you run **Login User**, so the next protected request uses the latest logged-in user.

## How to Add a New Request Manually

1. Right-click the collection or a folder.
2. Click **Add request**.
3. Give the request a clear name, for example `Update Task`.
4. Select the HTTP method, for example `PATCH`.
5. Enter the URL using the collection variable:

   ```text
   {{baseUrl}}/api/tasks/{{taskId}}/
   ```

6. If the request sends JSON, open **Body**, choose **raw**, choose **JSON**, and add the request data.
7. For protected endpoints, keep the collection-level authorization:

   ```text
   Bearer {{accessToken}}
   ```

8. Click **Save**.
9. Run the request.
10. To save an example response, click **Save Response** and choose **Save as example**.


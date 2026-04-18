from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from engagement.models import ActivityFeed, UserProfile


class TeamEngagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="team_user", password="StrongPass123!")
        self.client.force_authenticate(user=self.user)

    def test_team_project_and_project_task_rewards_are_applied_once(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Alpha Team", "description": "Study group"},
            format="json",
        )
        self.assertEqual(team_response.status_code, status.HTTP_201_CREATED)
        team_id = team_response.data["id"]

        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "Capstone", "description": "Backend work", "team": team_id},
            format="json",
        )
        self.assertEqual(project_response.status_code, status.HTTP_201_CREATED)
        project_id = project_response.data["id"]

        project_task_response = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Implement API", "status": "todo"},
            format="json",
        )
        self.assertEqual(project_task_response.status_code, status.HTTP_201_CREATED)
        project_task_id = project_task_response.data["id"]

        completion_response = self.client.patch(
            f"/api/teams/project-tasks/{project_task_id}/",
            {"status": "done"},
            format="json",
        )
        self.assertEqual(completion_response.status_code, status.HTTP_200_OK)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 42)
        self.assertEqual(ActivityFeed.objects.filter(actor=self.user, action_type="team_created").count(), 1)
        self.assertEqual(ActivityFeed.objects.filter(actor=self.user, action_type="project_created").count(), 1)
        self.assertEqual(ActivityFeed.objects.filter(actor=self.user, action_type="project_task_created").count(), 1)
        self.assertEqual(ActivityFeed.objects.filter(actor=self.user, action_type="project_task_completed").count(), 1)

        completion_entry = ActivityFeed.objects.get(actor=self.user, action_type="project_task_completed")
        self.assertEqual(completion_entry.xp_change, 12)

    def test_duplicate_project_title_in_same_team_is_rejected(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Unique Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        self.client.post(
            "/api/teams/projects/",
            {"title": "Capstone", "description": "Backend work", "team": team_id},
            format="json",
        )

        response = self.client.post(
            "/api/teams/projects/",
            {"title": "capstone", "description": "Duplicate", "team": team_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_duplicate_project_task_title_in_same_project_is_rejected(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Scoped Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "Platform", "description": "Backend work", "team": team_id},
            format="json",
        )
        project_id = project_response.data["id"]

        self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Implement API", "status": "todo"},
            format="json",
        )

        response = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "implement api", "status": "todo"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_project_task_status_can_be_updated_without_trailing_slash(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "No Slash Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "No Slash Project", "description": "Backend work", "team": team_id},
            format="json",
        )
        project_id = project_response.data["id"]

        project_task_response = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "No Slash Task", "status": "todo"},
            format="json",
        )
        project_task_id = project_task_response.data["id"]

        response = self.client.patch(
            f"/api/teams/project-tasks/{project_task_id}",
            {"status": "done"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_team_owner_can_add_members(self):
        owner = self.user
        member = User.objects.create_user(username="member_user", password="StrongPass123!")
        outsider = User.objects.create_user(username="outsider_user", password="StrongPass123!")

        team_response = self.client.post(
            "/api/teams/",
            {"name": "Owner Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        owner_add_response = self.client.post(
            f"/api/teams/{team_id}/members/",
            {"user": member.id, "role": "member"},
            format="json",
        )
        self.assertEqual(owner_add_response.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=member)
        member_add_response = self.client.post(
            f"/api/teams/{team_id}/members/",
            {"user": outsider.id, "role": "member"},
            format="json",
        )
        self.assertEqual(member_add_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_team_member_role_is_rejected(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Role Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]
        new_user = User.objects.create_user(username="role_user", password="StrongPass123!")

        response = self.client.post(
            f"/api/teams/{team_id}/members/",
            {"user": new_user.id, "role": "manager"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

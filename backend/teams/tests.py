from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from engagement.models import ActivityFeed, UserProfile
from teams.models import TeamMember
from users.models import Friendship


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
        self.assertEqual(profile.xp, 142)
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

    def test_project_task_priorities_are_normalized_and_drive_progress(self):
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Weighted Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]
        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "Weighted Project", "description": "Backend work", "team": team_id},
            format="json",
        )
        project_id = project_response.data["id"]

        first_task = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Research", "priority_points": 30},
            format="json",
        )
        self.assertEqual(first_task.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first_task.data["priority_points"], 100)

        second_task = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Build", "priority_points": 100},
            format="json",
        )
        self.assertEqual(second_task.status_code, status.HTTP_201_CREATED)

        tasks_response = self.client.get(f"/api/teams/projects/{project_id}/tasks/")
        self.assertEqual(tasks_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sum(task["priority_points"] for task in tasks_response.data), 100)
        build_task = next(task for task in tasks_response.data if task["title"] == "Build")

        complete_response = self.client.patch(
            f"/api/teams/project-tasks/{build_task['id']}/",
            {"status": "done"},
            format="json",
        )
        self.assertEqual(complete_response.status_code, status.HTTP_200_OK)

        project_detail = self.client.get(f"/api/teams/projects/{project_id}/")
        self.assertEqual(project_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(project_detail.data["progress_percent"], build_task["priority_points"])
        self.assertEqual(project_detail.data["status"], "active")

    def test_project_finishing_awards_contribution_xp_once(self):
        teammate = User.objects.create_user(username="weighted_teammate", password="StrongPass123!")
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Finish Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]
        self.client.post(f"/api/teams/{team_id}/members/", {"user": teammate.id}, format="json")
        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "Finish Project", "description": "Backend work", "team": team_id},
            format="json",
        )
        project_id = project_response.data["id"]
        task_one = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Owner work", "priority_points": 50},
            format="json",
        ).data
        task_two = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Member work", "priority_points": 50},
            format="json",
        ).data

        self.client.patch(f"/api/teams/project-tasks/{task_one['id']}/", {"status": "done"}, format="json")
        self.client.force_authenticate(user=teammate)
        self.client.patch(f"/api/teams/project-tasks/{task_two['id']}/", {"status": "done"}, format="json")

        project_detail = self.client.get(f"/api/teams/projects/{project_id}/")
        self.assertEqual(project_detail.data["status"], "finished")
        self.assertEqual(project_detail.data["progress_percent"], 100)
        self.assertGreater(UserProfile.objects.get(user=self.user).xp, 0)
        self.assertGreater(UserProfile.objects.get(user=teammate).xp, 0)

    def test_only_project_owner_can_delete_project_and_project_tasks(self):
        member = User.objects.create_user(username="delete_member", password="StrongPass123!")
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Delete Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]
        self.client.post(f"/api/teams/{team_id}/members/", {"user": member.id}, format="json")
        project_response = self.client.post(
            "/api/teams/projects/",
            {"title": "Delete Project", "description": "Backend work", "team": team_id},
            format="json",
        )
        project_id = project_response.data["id"]
        task_response = self.client.post(
            f"/api/teams/projects/{project_id}/tasks/",
            {"title": "Protected Task"},
            format="json",
        )
        task_id = task_response.data["id"]

        self.client.force_authenticate(user=member)
        self.assertEqual(self.client.delete(f"/api/teams/project-tasks/{task_id}/").status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f"/api/teams/projects/{project_id}/").status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.delete(f"/api/teams/project-tasks/{task_id}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.delete(f"/api/teams/projects/{project_id}/").status_code, status.HTTP_204_NO_CONTENT)

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

    def test_owner_can_invite_user_by_username_and_invitee_can_accept(self):
        invitee = User.objects.create_user(username="invitee_user", password="StrongPass123!")
        Friendship.objects.create(user_one=self.user, user_two=invitee)
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Invite Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        invite_response = self.client.post(
            "/api/teams/invitations/",
            {
                "invitee_username": "invitee_user",
                "team": team_id,
                "message": "Join us for the capstone sprint.",
            },
            format="json",
        )

        self.assertEqual(invite_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(invite_response.data["invitee_username"], "invitee_user")
        self.assertEqual(invite_response.data["status"], "pending")
        invitation_id = invite_response.data["id"]

        sent_response = self.client.get("/api/teams/invitations/")
        self.assertEqual(sent_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sent_response.data[0]["team_name"], "Invite Team")

        self.client.force_authenticate(user=invitee)
        received_response = self.client.get("/api/teams/received-invitations/")
        self.assertEqual(received_response.status_code, status.HTTP_200_OK)
        self.assertEqual(received_response.data[0]["inviter_username"], "team_user")

        accept_response = self.client.post(
            f"/api/teams/invitations/{invitation_id}/action/",
            {"action": "accept"},
            format="json",
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_response.data["status"], "accepted")
        self.assertTrue(TeamMember.objects.filter(team_id=team_id, user=invitee, role="member").exists())

    def test_non_owner_cannot_invite_user(self):
        owner = self.user
        member = User.objects.create_user(username="member_inviter", password="StrongPass123!")
        invitee = User.objects.create_user(username="blocked_invitee", password="StrongPass123!")
        Friendship.objects.create(user_one=member, user_two=invitee)
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Locked Invite Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]
        TeamMember.objects.create(team_id=team_id, user=member, role="member")

        self.client.force_authenticate(user=member)
        response = self.client.post(
            "/api/teams/invitations/",
            {"invitee_username": invitee.username, "team": team_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertTrue(TeamMember.objects.filter(team_id=team_id, user=owner, role="owner").exists())

    def test_duplicate_pending_invitation_is_rejected(self):
        invitee = User.objects.create_user(username="duplicate_invitee", password="StrongPass123!")
        Friendship.objects.create(user_one=self.user, user_two=invitee)
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Duplicate Invite Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        payload = {"invitee_username": invitee.username, "team": team_id}
        first_response = self.client.post("/api/teams/invitations/", payload, format="json")
        second_response = self.client.post("/api/teams/invitations/", payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", second_response.data)

    def test_project_invitation_shows_project_info_and_accept_adds_project_access(self):
        invitee = User.objects.create_user(username="project_invitee", password="StrongPass123!")
        Friendship.objects.create(user_one=self.user, user_two=invitee)
        team_response = self.client.post(
            "/api/teams/",
            {"name": "Project Invite Team", "description": "Study group"},
            format="json",
        )
        team_id = team_response.data["id"]

        project_response = self.client.post(
            "/api/teams/projects/",
            {
                "title": "Shared Sprint",
                "description": "Project invite details",
                "deadline": "2026-05-20",
                "team": team_id,
            },
            format="json",
        )
        project_id = project_response.data["id"]

        invite_response = self.client.post(
            "/api/teams/invitations/",
            {
                "invitee": invitee.id,
                "project": project_id,
                "message": "Join this project.",
            },
            format="json",
        )
        self.assertEqual(invite_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(invite_response.data["invitation_type"], "project")
        self.assertEqual(invite_response.data["project"], project_id)
        self.assertEqual(invite_response.data["project_title"], "Shared Sprint")
        self.assertEqual(invite_response.data["project_description"], "Project invite details")
        self.assertEqual(str(invite_response.data["project_deadline"]), "2026-05-20")
        invitation_id = invite_response.data["id"]

        self.client.force_authenticate(user=invitee)
        received_response = self.client.get("/api/teams/received-invitations/")
        self.assertEqual(received_response.status_code, status.HTTP_200_OK)
        self.assertEqual(received_response.data[0]["project_title"], "Shared Sprint")

        accept_response = self.client.post(
            f"/api/teams/invitations/{invitation_id}/action/",
            {"action": "accept"},
            format="json",
        )
        self.assertEqual(accept_response.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_response.data["status"], "accepted")

        projects_response = self.client.get("/api/teams/projects/")
        self.assertEqual(projects_response.status_code, status.HTTP_200_OK)
        self.assertEqual(projects_response.data[0]["id"], project_id)
        self.assertEqual(projects_response.data[0]["title"], "Shared Sprint")

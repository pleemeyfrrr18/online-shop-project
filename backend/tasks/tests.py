from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from engagement.models import ActivityFeed, UserProfile


class TaskEngagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="task_user", password="StrongPass123!")
        self.client.force_authenticate(user=self.user)

    def test_task_create_awards_xp_once_and_logs_one_activity(self):
        response = self.client.post(
            "/api/tasks/",
            {"title": "Read chapter 1", "status": "todo"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 5)
        self.assertEqual(
            ActivityFeed.objects.filter(actor=self.user, action_type="task_created").count(),
            1,
        )
        self.assertEqual(
            ActivityFeed.objects.get(actor=self.user, action_type="task_created").xp_change,
            5,
        )

    def test_task_completion_awards_xp_once_and_logs_one_completion(self):
        create_response = self.client.post(
            "/api/tasks/",
            {"title": "Finish homework", "status": "todo"},
            format="json",
        )
        task_id = create_response.data["id"]

        response = self.client.patch(
            f"/api/tasks/{task_id}/",
            {"status": "done"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 15)
        self.assertEqual(
            ActivityFeed.objects.filter(actor=self.user, action_type="task_completed").count(),
            1,
        )
        self.assertEqual(
            ActivityFeed.objects.get(actor=self.user, action_type="task_completed").xp_change,
            10,
        )

    def test_duplicate_task_title_for_same_user_is_rejected(self):
        self.client.post(
            "/api/tasks/",
            {"title": "Duplicate Name", "status": "todo"},
            format="json",
        )

        response = self.client.post(
            "/api/tasks/",
            {"title": "duplicate name", "status": "todo"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

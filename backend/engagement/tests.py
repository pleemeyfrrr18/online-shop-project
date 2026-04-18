from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Category, Task


class EngagementFeatureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eng_user", password="StrongPass123!")
        self.client.force_authenticate(user=self.user)

    def test_engagement_overview_returns_profile_and_badges(self):
        self.client.post("/api/tasks/", {"title": "Earn first badge"}, format="json")

        response = self.client.get("/api/engagement/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["username"], self.user.username)
        self.assertEqual(response.data["profile"]["xp"], 5)
        self.assertGreaterEqual(len(response.data["badges"]), 1)

    def test_suggestions_endpoint_returns_due_soon_personal_task(self):
        category = Category.objects.create(name="Math", user=self.user)
        Task.objects.create(
            title="Exam revision",
            user=self.user,
            category=category,
            status="todo",
            deadline=timezone.localdate() + timedelta(days=1),
        )

        response = self.client.get("/api/engagement/suggestions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suggestion_types = {item["type"] for item in response.data}
        self.assertIn("due_soon_task", suggestion_types)

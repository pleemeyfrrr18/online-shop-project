from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from engagement.models import UserProfile


class UserAuthAndProfileTests(APITestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "tester",
                "password": "StrongPass123!",
                "email": "tester@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="tester")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_endpoint_returns_engagement_profile(self):
        user = User.objects.create_user(username="profile_user", password="StrongPass123!")
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile", response.data)
        self.assertEqual(response.data["profile"]["xp"], 0)
        self.assertEqual(response.data["profile"]["level"], 1)

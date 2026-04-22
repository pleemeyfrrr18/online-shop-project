from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from engagement.models import UserProfile
from users.models import FriendRequest, Friendship


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

    def test_users_list_returns_other_registered_users(self):
        current_user = User.objects.create_user(username="current_user", password="StrongPass123!")
        other_user = User.objects.create_user(
            username="other_user",
            password="StrongPass123!",
            email="other@example.com",
        )
        self.client.force_authenticate(user=current_user)

        response = self.client.get("/api/users/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], other_user.id)
        self.assertEqual(response.data[0]["username"], "other_user")

    def test_friend_request_accept_creates_friendship(self):
        sender = User.objects.create_user(username="sender", password="StrongPass123!")
        receiver = User.objects.create_user(username="receiver", password="StrongPass123!")
        self.client.force_authenticate(user=sender)

        create_response = self.client.post(
            "/api/users/friend-requests/",
            {"to_user": receiver.id},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        request_id = create_response.data["id"]

        self.client.force_authenticate(user=receiver)
        action_response = self.client.post(
            f"/api/users/friend-requests/{request_id}/action/",
            {"action": "accept"},
            format="json",
        )
        self.assertEqual(action_response.status_code, status.HTTP_200_OK)
        self.assertEqual(action_response.data["request"]["status"], "accepted")
        self.assertEqual(Friendship.objects.count(), 1)

        friends_response = self.client.get("/api/users/friends/")
        self.assertEqual(friends_response.status_code, status.HTTP_200_OK)
        self.assertEqual(friends_response.data[0]["friend"]["username"], "sender")

        self.client.force_authenticate(user=sender)
        updates_response = self.client.get("/api/users/friend-requests/")
        self.assertEqual(updates_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updates_response.data["updates"][0]["status"], "accepted")
        self.assertEqual(updates_response.data["updates"][0]["to_user_username"], "receiver")

    def test_friend_request_decline_notifies_sender_without_friendship(self):
        sender = User.objects.create_user(username="declined_sender", password="StrongPass123!")
        receiver = User.objects.create_user(username="declining_receiver", password="StrongPass123!")
        friend_request = FriendRequest.objects.create(from_user=sender, to_user=receiver)
        self.client.force_authenticate(user=receiver)

        action_response = self.client.post(
            f"/api/users/friend-requests/{friend_request.id}/action/",
            {"action": "decline"},
            format="json",
        )
        self.assertEqual(action_response.status_code, status.HTTP_200_OK)
        self.assertEqual(action_response.data["request"]["status"], "declined")
        self.assertEqual(Friendship.objects.count(), 0)

        self.client.force_authenticate(user=sender)
        updates_response = self.client.get("/api/users/friend-requests/")
        self.assertEqual(updates_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updates_response.data["updates"][0]["status"], "declined")
        self.assertEqual(updates_response.data["updates"][0]["to_user_username"], "declining_receiver")

    def test_friend_request_cannot_target_self_or_duplicate_pending(self):
        sender = User.objects.create_user(username="duplicate_sender", password="StrongPass123!")
        receiver = User.objects.create_user(username="duplicate_receiver", password="StrongPass123!")
        self.client.force_authenticate(user=sender)

        self_response = self.client.post(
            "/api/users/friend-requests/",
            {"to_user": sender.id},
            format="json",
        )
        self.assertEqual(self_response.status_code, status.HTTP_400_BAD_REQUEST)

        first_response = self.client.post(
            "/api/users/friend-requests/",
            {"to_user": receiver.id},
            format="json",
        )
        second_response = self.client.post(
            "/api/users/friend-requests/",
            {"to_user": receiver.id},
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

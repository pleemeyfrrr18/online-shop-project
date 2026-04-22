from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Friendship(models.Model):
    user_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_as_user_one")
    user_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_as_user_two")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_one", "user_two"], name="unique_friendship_pair"),
            models.CheckConstraint(
                condition=~models.Q(user_one=models.F("user_two")),
                name="friendship_users_must_differ",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user_one_id and self.user_two_id and self.user_one_id > self.user_two_id:
            self.user_one_id, self.user_two_id = self.user_two_id, self.user_one_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_one.username} and {self.user_two.username}"


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="unique_friend_request_direction"),
            models.CheckConstraint(
                condition=~models.Q(from_user=models.F("to_user")),
                name="friend_request_users_must_differ",
            ),
        ]

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"

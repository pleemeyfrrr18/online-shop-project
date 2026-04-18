from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="engagement_profile")
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def save(self, *args, **kwargs):
        # Automatically recalculate level based on XP
        from .utils import calculate_level
        self.level = calculate_level(self.xp)
        super().save(*args, **kwargs)


class Badge(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    xp_threshold = models.PositiveIntegerField(default=0)
    level_threshold = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["xp_threshold", "level_threshold", "id"]

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="earned_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awarded_users")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class ActivityFeed(models.Model):
    ACTION_CHOICES = [
        ("task_created", "Task Created"),
        ("task_completed", "Task Completed"),
        ("team_created", "Team Created"),
        ("project_created", "Project Created"),
        ("project_task_created", "Project Task Created"),
        ("project_task_completed", "Project Task Completed"),
        ("badge_awarded", "Badge Awarded"),
        ("level_up", "Level Up"),
    ]

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_entries")
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    message = models.CharField(max_length=255)
    xp_change = models.IntegerField(default=0)
    team = models.ForeignKey("teams.Team", on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_entries")
    project = models.ForeignKey("teams.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_entries")
    task = models.ForeignKey("tasks.Task", on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_entries")
    project_task = models.ForeignKey(
        "teams.ProjectTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_entries",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.actor.username} - {self.action_type}"

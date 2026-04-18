from django.contrib.auth.models import User
from rest_framework import serializers

from .models import ActivityFeed, Badge, UserBadge, UserProfile


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["xp", "level", "created_at", "updated_at"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "code", "name", "description", "xp_threshold", "level_threshold", "created_at"]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model = UserBadge
        fields = ["id", "badge", "awarded_at"]


class ActivityFeedSerializer(serializers.ModelSerializer):
    actor = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ActivityFeed
        fields = [
            "id",
            "actor",
            "action_type",
            "message",
            "xp_change",
            "team",
            "project",
            "task",
            "project_task",
            "created_at",
        ]


class EngagementOverviewSerializer(serializers.Serializer):
    user = SimpleUserSerializer()
    profile = UserProfileSerializer()
    badges = UserBadgeSerializer(many=True)


class SuggestionSerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    priority = serializers.CharField()
    source = serializers.CharField()
    object_id = serializers.IntegerField(required=False, allow_null=True)

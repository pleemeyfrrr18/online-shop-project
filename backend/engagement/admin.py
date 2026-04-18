from django.contrib import admin

from .models import ActivityFeed, Badge, UserBadge, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "xp", "level", "updated_at")
    search_fields = ("user__username", "user__email")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "xp_threshold", "level_threshold", "created_at")
    search_fields = ("code", "name")


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "awarded_at")
    search_fields = ("user__username", "badge__name")


@admin.register(ActivityFeed)
class ActivityFeedAdmin(admin.ModelAdmin):
    list_display = ("actor", "action_type", "xp_change", "created_at")
    list_filter = ("action_type", "created_at")
    search_fields = ("actor__username", "message")

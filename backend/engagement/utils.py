from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import ActivityFeed, Badge, UserBadge, UserProfile


XP_PER_LEVEL = 100

DEFAULT_BADGES = [
    {
        "code": "first_steps",
        "name": "First Steps",
        "description": "Earn at least 5 XP.",
        "xp_threshold": 5,
        "level_threshold": 1,
    },
    {
        "code": "starter",
        "name": "Starter",
        "description": "Earn at least 25 XP.",
        "xp_threshold": 25,
        "level_threshold": 1,
    },
    {
        "code": "focused",
        "name": "Focused",
        "description": "Earn at least 50 XP.",
        "xp_threshold": 50,
        "level_threshold": 1,
    },
    {
        "code": "level_two",
        "name": "Level Two",
        "description": "Reach level 2.",
        "xp_threshold": 0,
        "level_threshold": 2,
    },
    {
        "code": "level_three",
        "name": "Level Three",
        "description": "Reach level 3.",
        "xp_threshold": 0,
        "level_threshold": 3,
    },
]


def ensure_default_badges():
    for badge_data in DEFAULT_BADGES:
        Badge.objects.get_or_create(code=badge_data["code"], defaults=badge_data)


def calculate_level(xp):
    return max(1, (xp // XP_PER_LEVEL) + 1)


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def log_activity(actor, action_type, message, xp_change=0, team=None, project=None, task=None, project_task=None):
    return ActivityFeed.objects.create(
        actor=actor,
        action_type=action_type,
        message=message,
        xp_change=xp_change,
        team=team,
        project=project,
        task=task,
        project_task=project_task,
    )


def award_badges(user):
    ensure_default_badges()
    profile = get_or_create_profile(user)
    awarded = []

    for badge in Badge.objects.all():
        if profile.xp < badge.xp_threshold or profile.level < badge.level_threshold:
            continue
        user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
        if created:
            awarded.append(user_badge)
            log_activity(
                actor=user,
                action_type="badge_awarded",
                message=f'Badge unlocked: "{badge.name}".',
                xp_change=0,
            )
    return awarded


@transaction.atomic
def award_xp(user, amount):
    profile = get_or_create_profile(user)
    previous_level = profile.level
    profile.xp += amount
    profile.level = calculate_level(profile.xp)
    profile.save(update_fields=["xp", "level", "updated_at"])

    if profile.level > previous_level:
        log_activity(
            actor=user,
            action_type="level_up",
            message=f"Reached level {profile.level}.",
            xp_change=0,
        )

    award_badges(user)
    return profile


def build_suggestions(user):
    from tasks.models import Task
    from teams.models import ProjectTask

    today = timezone.localdate()
    soon = today + timedelta(days=3)
    suggestions = []

    overdue_tasks = Task.objects.filter(user=user, status__in=["todo", "doing"], deadline__lt=today).order_by("deadline")
    for task in overdue_tasks[:3]:
        suggestions.append(
            {
                "type": "overdue_task",
                "title": "Overdue personal task",
                "message": f'"{task.title}" is overdue. Consider finishing it first.',
                "priority": "high",
                "source": "tasks",
                "object_id": task.id,
            }
        )

    due_soon_tasks = Task.objects.filter(
        user=user,
        status__in=["todo", "doing"],
        deadline__gte=today,
        deadline__lte=soon,
    ).order_by("deadline")
    for task in due_soon_tasks[:3]:
        suggestions.append(
            {
                "type": "due_soon_task",
                "title": "Task due soon",
                "message": f'"{task.title}" is due soon. This is a good next task to focus on.',
                "priority": "medium",
                "source": "tasks",
                "object_id": task.id,
            }
        )

    category_counts = {}
    for task in Task.objects.filter(user=user, status__in=["todo", "doing"]).select_related("category"):
        category_name = task.category.name if task.category else "Uncategorized"
        category_counts[category_name] = category_counts.get(category_name, 0) + 1
    if category_counts:
        focus_category = max(category_counts, key=category_counts.get)
        suggestions.append(
            {
                "type": "focus_category",
                "title": "Suggested focus area",
                "message": f"You have the most unfinished work in {focus_category}. Focusing there could reduce backlog faster.",
                "priority": "medium",
                "source": "tasks",
                "object_id": None,
            }
        )

    overdue_project_tasks = ProjectTask.objects.filter(
        assigned_user=user,
        status__in=["todo", "doing"],
        deadline__lt=today,
    ).select_related("project").order_by("deadline")
    for project_task in overdue_project_tasks[:3]:
        suggestions.append(
            {
                "type": "overdue_project_task",
                "title": "Overdue project task",
                "message": f'"{project_task.title}" in project "{project_task.project.title}" needs attention.',
                "priority": "high",
                "source": "project_tasks",
                "object_id": project_task.id,
            }
        )

    due_soon_project_tasks = ProjectTask.objects.filter(
        assigned_user=user,
        status__in=["todo", "doing"],
        deadline__gte=today,
        deadline__lte=soon,
    ).select_related("project").order_by("deadline")
    for project_task in due_soon_project_tasks[:3]:
        suggestions.append(
            {
                "type": "due_soon_project_task",
                "title": "Project task due soon",
                "message": f'"{project_task.title}" in "{project_task.project.title}" is due soon.',
                "priority": "medium",
                "source": "project_tasks",
                "object_id": project_task.id,
            }
        )

    if not suggestions:
        suggestions.append(
            {
                "type": "on_track",
                "title": "You are on track",
                "message": "No urgent items found. Keep your momentum going.",
                "priority": "low",
                "source": "system",
                "object_id": None,
            }
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda item: (priority_order.get(item["priority"], 3), item["title"]))
    return suggestions[:10]

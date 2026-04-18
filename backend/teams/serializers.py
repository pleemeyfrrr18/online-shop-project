from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team, TeamMember, Project, ProjectTask


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class TeamSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source="creator.username", read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "description", "creator", "creator_username", "created_at"]
        read_only_fields = ["creator", "created_at"]


class TeamMemberSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = TeamMember
        fields = ["id", "team", "team_name", "user", "user_username", "role"]


class ProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    def validate(self, attrs):
        team = attrs.get("team") or getattr(self.instance, "team", None)
        title = attrs.get("title") or getattr(self.instance, "title", None)

        if team and title:
            queryset = Project.objects.filter(team=team, title__iexact=title)
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"title": "This team already has a project with this title."})

        return attrs

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "team",
            "team_name",
            "created_by",
            "created_by_username",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


class ProjectTaskSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    assigned_user_username = serializers.CharField(source="assigned_user.username", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    def validate(self, attrs):
        project = attrs.get("project") or getattr(self.instance, "project", None)
        title = attrs.get("title") or getattr(self.instance, "title", None)

        if project and title:
            queryset = ProjectTask.objects.filter(project=project, title__iexact=title)
            if self.instance is not None:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"title": "This project already has a task with this title."})

        return attrs

    class Meta:
        model = ProjectTask
        fields = [
            "id",
            "title",
            "description",
            "status",
            "deadline",
            "project",
            "project_title",
            "assigned_user",
            "assigned_user_username",
            "created_by",
            "created_by_username",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

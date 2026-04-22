from django.contrib.auth.models import User
from rest_framework import serializers
from django.db import models
from .models import Team, TeamMember, Project, ProjectTask, JoinRequest, Invitation
from users.models import Friendship


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
    progress_percent = serializers.SerializerMethodField()

    def get_progress_percent(self, obj):
        tasks = obj.tasks.all()
        total_points = sum(task.priority_points for task in tasks)
        if total_points <= 0:
            return 0
        completed_points = sum(task.priority_points for task in tasks if task.status == "done")
        return round((completed_points / total_points) * 100)

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
            "status",
            "progress_percent",
            "team",
            "team_name",
            "created_by",
            "created_by_username",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["created_by", "created_at", "completed_at", "status"]


class ProjectTaskSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    assigned_user_username = serializers.CharField(source="assigned_user.username", read_only=True)
    completed_by_username = serializers.CharField(source="completed_by.username", read_only=True)
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
            "priority_points",
            "project",
            "project_title",
            "assigned_user",
            "assigned_user_username",
            "completed_by",
            "completed_by_username",
            "created_by",
            "created_by_username",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at", "completed_by"]

    def validate_priority_points(self, value):
        if value > 100:
            raise serializers.ValidationError("Priority points must be between 0 and 100.")
        return value
class JoinRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source="requester.username", read_only=True)
    target_title = serializers.ReadOnlyField()
    target_creator_username = serializers.SerializerMethodField()

    def get_target_creator_username(self, obj):
        return obj.target_creator.username

    class Meta:
        model = JoinRequest
        fields = [
            "id",
            "request_type",
            "status",
            "requester",
            "requester_username",
            "team",
            "project",
            "target_title",
            "target_creator_username",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["requester", "created_at", "updated_at"]


class CreateJoinRequestSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context['request'].user
        team = attrs.get('team')
        project = attrs.get('project')

        # Check if user is already a member
        if team:
            if TeamMember.objects.filter(team=team, user=user).exists():
                raise serializers.ValidationError("You are already a member of this team.")
        elif project:
            # Check if user is a member of the project's team
            if TeamMember.objects.filter(team=project.team, user=user).exists():
                raise serializers.ValidationError("You are already a member of this project's team.")

        # Check if there's already a pending request
        existing_request = JoinRequest.objects.filter(
            requester=user,
            status='pending'
        ).filter(
            models.Q(team=team) if team else models.Q(project=project)
        ).exists()

        if existing_request:
            raise serializers.ValidationError("You already have a pending request for this target.")

        return attrs

    class Meta:
        model = JoinRequest
        fields = ["request_type", "team", "project", "message"]


class PublicProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    member_count = serializers.SerializerMethodField()
    has_pending_request = serializers.SerializerMethodField()

    def get_member_count(self, obj):
        return TeamMember.objects.filter(team=obj.team).count()

    def get_has_pending_request(self, obj):
        user = self.context.get('request', {}).user if hasattr(self.context.get('request'), 'user') else None
        if user and user.is_authenticated:
            return JoinRequest.objects.filter(
                requester=user,
                project=obj,
                status='pending'
            ).exists()
        return False

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "deadline",
            "team_name",
            "created_by_username",
            "member_count",
            "has_pending_request",
            "created_at",
        ]


class InvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(source="inviter.username", read_only=True)
    invitee_username = serializers.CharField(source="invitee.username", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    project_title = serializers.SerializerMethodField()
    project_description = serializers.SerializerMethodField()
    project_deadline = serializers.SerializerMethodField()
    invitation_type = serializers.SerializerMethodField()

    def get_invitation_type(self, obj):
        return "project" if obj.project_id else "team"

    def get_project_title(self, obj):
        return obj.project.title if obj.project_id else None

    def get_project_description(self, obj):
        return obj.project.description if obj.project_id else None

    def get_project_deadline(self, obj):
        return obj.project.deadline if obj.project_id else None

    class Meta:
        model = Invitation
        fields = [
            "id",
            "inviter",
            "inviter_username",
            "invitee",
            "invitee_username",
            "team",
            "team_name",
            "project",
            "project_title",
            "project_description",
            "project_deadline",
            "invitation_type",
            "status",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["inviter", "created_at", "updated_at"]


class CreateInvitationSerializer(serializers.ModelSerializer):
    invitee_username = serializers.CharField(write_only=True, required=False, allow_blank=False)

    def validate(self, attrs):
        user = self.context['request'].user
        team = attrs.get('team')
        project = attrs.get('project')
        invitee = attrs.get('invitee')
        invitee_username = attrs.pop('invitee_username', None)

        if project:
            attrs['team'] = project.team
            team = project.team

        if team is None:
            raise serializers.ValidationError({"team": "Team is required."})

        if invitee is None and invitee_username:
            try:
                invitee = User.objects.get(username__iexact=invitee_username.strip())
            except User.DoesNotExist:
                raise serializers.ValidationError({"invitee_username": "No user was found with this username."})
            attrs['invitee'] = invitee

        if invitee is None:
            raise serializers.ValidationError({"invitee": "Invitee is required."})

        if invitee == user:
            raise serializers.ValidationError({"detail": "You cannot invite yourself."})

        first_user_id, second_user_id = sorted([user.id, invitee.id])
        if not Friendship.objects.filter(user_one_id=first_user_id, user_two_id=second_user_id).exists():
            raise serializers.ValidationError({"detail": "You can only invite friends."})

        if project and not TeamMember.objects.filter(team=team, user=user).exists():
            raise serializers.ValidationError({"detail": "Only project team members can send project invitations."})

        if not project and not TeamMember.objects.filter(team=team, user=user, role='owner').exists():
            raise serializers.ValidationError({"detail": "Only team owners can send invitations."})

        # Check if invitee is already a member
        if TeamMember.objects.filter(team=team, user=invitee).exists():
            target = "project's team" if project else "team"
            raise serializers.ValidationError({"detail": f"This user is already a member of the {target}."})

        # Check if invitation already exists
        pending_invitations = Invitation.objects.filter(invitee=invitee, status='pending')
        if project:
            pending_invitations = pending_invitations.filter(project=project)
        else:
            pending_invitations = pending_invitations.filter(team=team, project__isnull=True)

        if pending_invitations.exists():
            raise serializers.ValidationError({"detail": "An invitation is already pending for this user."})

        previous_invitations = Invitation.objects.filter(invitee=invitee, inviter=user)
        if project:
            previous_invitations = previous_invitations.filter(project=project)
        else:
            previous_invitations = previous_invitations.filter(team=team, project__isnull=True)

        if previous_invitations.exists():
            target = "project" if project else "team"
            raise serializers.ValidationError({"detail": f"You have already invited this user to this {target}."})

        return attrs

    class Meta:
        model = Invitation
        fields = ["invitee", "invitee_username", "team", "project", "message"]
        extra_kwargs = {
            "invitee": {"required": False},
            "team": {"required": False},
        }

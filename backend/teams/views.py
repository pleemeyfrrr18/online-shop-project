from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Team, TeamMember, Project, ProjectTask
from .serializers import (
    TeamSerializer,
    TeamMemberSerializer,
    ProjectSerializer,
    ProjectTaskSerializer,
)
from engagement.utils import award_xp, log_activity


def user_is_team_member(user, team):
    return TeamMember.objects.filter(team=team, user=user).exists()


def user_is_team_owner(user, team):
    return TeamMember.objects.filter(team=team, user=user, role="owner").exists()


class TeamListCreateAPIView(ListCreateAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.filter(team__user=self.request.user).distinct().order_by("-id")

    def perform_create(self, serializer):
        team = serializer.save(creator=self.request.user)
        TeamMember.objects.create(team=team, user=self.request.user, role="owner")
        award_xp(self.request.user, 15)
        log_activity(
            actor=self.request.user,
            action_type="team_created",
            message=f'Team created: "{team.name}".',
            xp_change=15,
            team=team,
        )


class TeamDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.filter(team__user=self.request.user).distinct()


class TeamMemberListCreateAPIView(APIView):
    def get(self, request, team_id):
        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user_is_team_member(request.user, team):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        members = TeamMember.objects.filter(team=team).select_related("user", "team")
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request, team_id):
        try:
            team = Team.objects.get(pk=team_id)
        except Team.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user_is_team_owner(request.user, team):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user")
        role = request.data.get("role", "member")
        allowed_roles = {choice[0] for choice in TeamMember.ROLE_CHOICES}

        if not user_id:
            return Response({"detail": "User field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if role not in allowed_roles:
            return Response(
                {"detail": f"Role must be one of: {', '.join(sorted(allowed_roles))}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response({"detail": "User is already in this team."}, status=status.HTTP_400_BAD_REQUEST)

        member = TeamMember.objects.create(team=team, user=user, role=role)
        serializer = TeamMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectListCreateAPIView(ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(team__team__user=self.request.user).distinct().order_by("-id")

    def perform_create(self, serializer):
        team = serializer.validated_data["team"]
        if not user_is_team_member(self.request.user, team):
            raise PermissionError("You are not a member of this team.")
        project = serializer.save(created_by=self.request.user)
        award_xp(self.request.user, 10)
        log_activity(
            actor=self.request.user,
            action_type="project_created",
            message=f'Project created: "{project.title}".',
            xp_change=10,
            team=project.team,
            project=project,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        team = serializer.validated_data["team"]
        if not user_is_team_member(request.user, team):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(team__team__user=self.request.user).distinct()


class ProjectTaskListCreateAPIView(ListCreateAPIView):
    serializer_class = ProjectTaskSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return ProjectTask.objects.filter(
            project_id=project_id,
            project__team__team__user=self.request.user,
        ).distinct().order_by("-id")

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs["project_id"]

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user_is_team_member(request.user, project.team):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data["project"] = project_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        assigned_user = serializer.validated_data.get("assigned_user")
        if assigned_user and not TeamMember.objects.filter(team=project.team, user=assigned_user).exists():
            return Response(
                {"detail": "Assigned user is not a member of this team."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_task = serializer.save(created_by=request.user)
        award_xp(request.user, 5)
        log_activity(
            actor=request.user,
            action_type="project_task_created",
            message=f'Project task created: "{project_task.title}".',
            xp_change=5,
            team=project.team,
            project=project,
            project_task=project_task,
        )
        return Response(self.get_serializer(project_task).data, status=status.HTTP_201_CREATED)


class ProjectTaskDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectTaskSerializer

    def get_queryset(self):
        return ProjectTask.objects.filter(
            project__team__team__user=self.request.user
        ).distinct()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        previous_status = instance.status

        assigned_user_id = request.data.get("assigned_user")
        if assigned_user_id:
            if not TeamMember.objects.filter(team=instance.project.team, user_id=assigned_user_id).exists():
                return Response(
                    {"detail": "Assigned user is not a member of this team."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()

        if previous_status != "done" and instance.status == "done":
            award_xp(request.user, 12)
            log_activity(
                actor=request.user,
                action_type="project_task_completed",
                message=f'Project task completed: "{instance.title}".',
                xp_change=12,
                team=instance.project.team,
                project=instance.project,
                project_task=instance,
            )

        return response

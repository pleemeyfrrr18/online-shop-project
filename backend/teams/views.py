from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Team, TeamMember, Project, ProjectTask, JoinRequest, Invitation
from .serializers import (
    TeamSerializer,
    TeamMemberSerializer,
    ProjectSerializer,
    ProjectTaskSerializer,
    JoinRequestSerializer,
    CreateJoinRequestSerializer,
    PublicProjectSerializer,
    InvitationSerializer,
    CreateInvitationSerializer,
)
from engagement.utils import award_xp, log_activity


def user_is_team_member(user, team):
    return TeamMember.objects.filter(team=team, user=user).exists()


def user_is_team_owner(user, team):
    return TeamMember.objects.filter(team=team, user=user, role="owner").exists()


def normalize_project_task_priorities(project):
    tasks = list(ProjectTask.objects.filter(project=project).order_by("id"))
    if not tasks:
        return

    if len(tasks) == 1:
        task = tasks[0]
        if task.priority_points != 100:
            task.priority_points = 100
            task.save(update_fields=["priority_points"])
        return

    total = sum(task.priority_points for task in tasks)
    if total <= 0:
        base = 100 // len(tasks)
        remainder = 100 - (base * len(tasks))
        for index, task in enumerate(tasks):
            task.priority_points = base + (1 if index < remainder else 0)
            task.save(update_fields=["priority_points"])
        return

    scaled = []
    for task in tasks:
        exact = task.priority_points * 100 / total
        floor_value = int(exact)
        scaled.append((task, floor_value, exact - floor_value))

    remainder = 100 - sum(item[1] for item in scaled)
    scaled.sort(key=lambda item: item[2], reverse=True)
    for index, (task, floor_value, _fraction) in enumerate(scaled):
        task.priority_points = floor_value + (1 if index < remainder else 0)
        task.save(update_fields=["priority_points"])


def refresh_project_completion(project):
    tasks = list(ProjectTask.objects.filter(project=project).select_related("completed_by", "assigned_user", "created_by"))
    if not tasks:
        if project.status != "active":
            project.status = "active"
            project.completed_at = None
            project.save(update_fields=["status", "completed_at"])
        return

    is_finished = all(task.status == "done" for task in tasks)
    if not is_finished:
        if project.status != "active":
            project.status = "active"
            project.completed_at = None
            project.save(update_fields=["status", "completed_at"])
        return

    update_fields = []
    if project.status != "finished":
        project.status = "finished"
        project.completed_at = timezone.now()
        update_fields.extend(["status", "completed_at"])

    if project.xp_awarded_at is None:
        contributions = {}
        for task in tasks:
            contributor = task.completed_by or task.assigned_user or task.created_by
            contributions[contributor] = contributions.get(contributor, 0) + task.priority_points

        for contributor, points in contributions.items():
            award_xp(contributor, points)
            log_activity(
                actor=contributor,
                action_type="project_completed",
                message=f'Project completed: "{project.title}" ({points} contribution XP).',
                xp_change=points,
                team=project.team,
                project=project,
            )

        project.xp_awarded_at = timezone.now()
        update_fields.append("xp_awarded_at")

    if update_fields:
        project.save(update_fields=update_fields)


class TeamListCreateAPIView(ListCreateAPIView):
    serializer_class = TeamSerializer

    def get_queryset(self):
        # Return teams where the user is a member
        return Team.objects.filter(
            team__user=self.request.user
        ).distinct().order_by("-id")

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
    lookup_field = 'pk'

    def get_queryset(self):
        # Return teams where the user is a member
        return Team.objects.filter(team__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if not user_is_team_owner(request.user, team):
            return Response({"detail": "Only team owners can delete this team."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


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
        # Return projects from teams where the user is a member
        return Project.objects.filter(
            team__team__user=self.request.user
        ).select_related('team', 'created_by').distinct().order_by("-id")

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
        # Return projects from teams where the user is a member
        return Project.objects.filter(team__team__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        if project.created_by != request.user:
            return Response({"detail": "Only the project owner can delete this project."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


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

        completed_by = request.user if serializer.validated_data.get("status") == "done" else None
        project_task = serializer.save(created_by=request.user, completed_by=completed_by)
        normalize_project_task_priorities(project)
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
        refresh_project_completion(project)
        project_task.refresh_from_db()
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

        update_fields = []
        if previous_status != "done" and instance.status == "done" and instance.completed_by_id is None:
            instance.completed_by = request.user
            update_fields.append("completed_by")
        elif previous_status == "done" and instance.status != "done" and instance.completed_by_id is not None:
            instance.completed_by = None
            update_fields.append("completed_by")

        if update_fields:
            instance.save(update_fields=update_fields)
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

        normalize_project_task_priorities(instance.project)
        refresh_project_completion(instance.project)
        instance.refresh_from_db()
        response.data = self.get_serializer(instance).data
        return response

    def destroy(self, request, *args, **kwargs):
        project_task = self.get_object()
        project = project_task.project
        if project.created_by != request.user:
            return Response({"detail": "Only the project owner can delete project tasks."}, status=status.HTTP_403_FORBIDDEN)
        response = super().destroy(request, *args, **kwargs)
        normalize_project_task_priorities(project)
        refresh_project_completion(project)
        return response


class PublicProjectListAPIView(ListCreateAPIView):
    serializer_class = PublicProjectSerializer

    def get_queryset(self):
        # Return projects that are public (not private)
        return Project.objects.filter(is_private=False).select_related('team', 'creator').order_by('-created_at')


class JoinRequestListCreateAPIView(ListCreateAPIView):
    serializer_class = CreateJoinRequestSerializer

    def get_queryset(self):
        return JoinRequest.objects.filter(requester=self.request.user).select_related('project', 'project__team')

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class JoinRequestDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = JoinRequestSerializer

    def get_queryset(self):
        return JoinRequest.objects.filter(requester=self.request.user)


class ReceivedJoinRequestsAPIView(ListCreateAPIView):
    serializer_class = JoinRequestSerializer

    def get_queryset(self):
        # Return join requests for projects created by the user or where user is team owner
        from django.db.models import Q
        return JoinRequest.objects.filter(
            Q(project__created_by=self.request.user) |
            Q(project__team__creator=self.request.user)
        ).select_related('requester', 'project', 'project__team').order_by('-created_at')


class JoinRequestActionAPIView(APIView):
    def post(self, request, request_id):
        from django.db.models import Q
        try:
            join_request = JoinRequest.objects.get(
                id=request_id,
                project__created_by=request.user
            )
        except JoinRequest.DoesNotExist:
            # Try checking if user is team owner
            try:
                join_request = JoinRequest.objects.get(
                    id=request_id,
                    project__team__creator=request.user
                )
            except JoinRequest.DoesNotExist:
                return Response({"detail": "Join request not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action not in ['accept', 'decline']:
            return Response({"detail": "Invalid action. Must be 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)

        if join_request.status != 'pending':
            return Response({"detail": "This join request has already been processed."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            # Add user to the team
            TeamMember.objects.get_or_create(
                team=join_request.project.team,
                user=join_request.requester,
                defaults={'role': 'member'}
            )
            join_request.status = 'accepted'
            message = f'Join request accepted. {join_request.requester.username} has been added to the team.'
        else:
            join_request.status = 'declined'
            message = f'Join request declined for {join_request.requester.username}.'

        join_request.save()

        # Log activity
        log_activity(
            actor=request.user,
            action_type="join_request_responded",
            message=message,
            team=join_request.project.team,
            project=join_request.project,
        )

        return Response({"detail": message, "status": join_request.status})


class InvitationListCreateAPIView(ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateInvitationSerializer
        return InvitationSerializer

    def get_queryset(self):
        # Return invitations sent by the user
        return Invitation.objects.filter(inviter=self.request.user).select_related(
            "inviter",
            "invitee",
            "team",
            "project",
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(inviter=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save(inviter=request.user)
        response_serializer = InvitationSerializer(invitation, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReceivedInvitationsAPIView(ListAPIView):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        # Return invitations received by the user
        return Invitation.objects.filter(invitee=self.request.user).select_related('inviter', 'team', 'project').order_by('-created_at')


class InvitationDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return Invitation.objects.filter(invitee=self.request.user)


class InvitationActionAPIView(APIView):
    def post(self, request, invitation_id):
        try:
            invitation = Invitation.objects.get(
                id=invitation_id,
                invitee=request.user
            )
        except Invitation.DoesNotExist:
            return Response({"detail": "Invitation not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action not in ['accept', 'decline']:
            return Response({"detail": "Invalid action. Must be 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.status != 'pending':
            return Response({"detail": "This invitation has already been processed."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            # Add user to the team
            TeamMember.objects.get_or_create(
                team=invitation.team,
                user=invitation.invitee,
                defaults={'role': 'member'}
            )
            invitation.status = 'accepted'
            if invitation.project:
                message = f'Invitation accepted. {invitation.project.title} has been added to your projects.'
            else:
                message = f'Invitation accepted. You have been added to {invitation.team.name}.'
        else:
            invitation.status = 'declined'
            message = f'Invitation declined.'

        invitation.save()

        # Log activity
        log_activity(
            actor=request.user,
            action_type="invitation_responded",
            message=message,
            team=invitation.team,
            project=invitation.project,
        )

        return Response({"detail": message, "status": invitation.status})

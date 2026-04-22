from django.urls import path
from .views import (
    TeamListCreateAPIView,
    TeamDetailAPIView,
    TeamMemberListCreateAPIView,
    ProjectListCreateAPIView,
    ProjectDetailAPIView,
    ProjectTaskListCreateAPIView,
    ProjectTaskDetailAPIView,
    PublicProjectListAPIView,
    JoinRequestListCreateAPIView,
    JoinRequestDetailAPIView,
    ReceivedJoinRequestsAPIView,
    JoinRequestActionAPIView,
    InvitationListCreateAPIView,
    ReceivedInvitationsAPIView,
    InvitationDetailAPIView,
    InvitationActionAPIView,
)

urlpatterns = [
    path("", TeamListCreateAPIView.as_view()),
    path("<int:pk>", TeamDetailAPIView.as_view()),
    path("<int:pk>/", TeamDetailAPIView.as_view()),
    path("<int:team_id>/members", TeamMemberListCreateAPIView.as_view()),
    path("<int:team_id>/members/", TeamMemberListCreateAPIView.as_view()),

    path("projects", ProjectListCreateAPIView.as_view()),
    path("projects/", ProjectListCreateAPIView.as_view()),
    path("projects/<int:pk>", ProjectDetailAPIView.as_view()),
    path("projects/<int:pk>/", ProjectDetailAPIView.as_view()),

    path("projects/<int:project_id>/tasks", ProjectTaskListCreateAPIView.as_view()),
    path("projects/<int:project_id>/tasks/", ProjectTaskListCreateAPIView.as_view()),
    path("project-tasks/<int:pk>", ProjectTaskDetailAPIView.as_view()),
    path("project-tasks/<int:pk>/", ProjectTaskDetailAPIView.as_view()),

    # Public project browsing
    path("public-projects", PublicProjectListAPIView.as_view()),
    path("public-projects/", PublicProjectListAPIView.as_view()),

    # Join requests
    path("join-requests", JoinRequestListCreateAPIView.as_view()),
    path("join-requests/", JoinRequestListCreateAPIView.as_view()),
    path("join-requests/<int:pk>", JoinRequestDetailAPIView.as_view()),
    path("join-requests/<int:pk>/", JoinRequestDetailAPIView.as_view()),
    path("join-requests/<int:pk>/action", JoinRequestActionAPIView.as_view()),
    path("join-requests/<int:pk>/action/", JoinRequestActionAPIView.as_view()),

    # Received join requests (for creators)
    path("received-join-requests", ReceivedJoinRequestsAPIView.as_view()),
    path("received-join-requests/", ReceivedJoinRequestsAPIView.as_view()),

    # Invitations
    path("invitations", InvitationListCreateAPIView.as_view()),
    path("invitations/", InvitationListCreateAPIView.as_view()),
    path("invitations/<int:pk>", InvitationDetailAPIView.as_view()),
    path("invitations/<int:pk>/", InvitationDetailAPIView.as_view()),
    path("invitations/<int:invitation_id>/action", InvitationActionAPIView.as_view()),
    path("invitations/<int:invitation_id>/action/", InvitationActionAPIView.as_view()),

    # Received invitations
    path("received-invitations", ReceivedInvitationsAPIView.as_view()),
    path("received-invitations/", ReceivedInvitationsAPIView.as_view()),
]

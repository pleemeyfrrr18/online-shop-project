from django.urls import path
from .views import (
    TeamListCreateAPIView,
    TeamDetailAPIView,
    TeamMemberListCreateAPIView,
    ProjectListCreateAPIView,
    ProjectDetailAPIView,
    ProjectTaskListCreateAPIView,
    ProjectTaskDetailAPIView,
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
]

from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    TaskListCreateAPIView,
    TaskDetailAPIView
)

urlpatterns = [
    path('categories', CategoryListCreateAPIView.as_view()),
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:pk>', CategoryDetailAPIView.as_view()),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view()),
    path('', TaskListCreateAPIView.as_view()),
    path('<int:pk>', TaskDetailAPIView.as_view()),
    path('<int:pk>/', TaskDetailAPIView.as_view()),
]

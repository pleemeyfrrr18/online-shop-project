from django.urls import path

from .views import (
    ActivityFeedListAPIView,
    BadgeListAPIView,
    EngagementOverviewAPIView,
    SmartSuggestionsAPIView,
    UserProfileAPIView,
)

urlpatterns = [
    path("", EngagementOverviewAPIView.as_view()),
    path("profile", UserProfileAPIView.as_view()),
    path("profile/", UserProfileAPIView.as_view()),
    path("badges", BadgeListAPIView.as_view()),
    path("badges/", BadgeListAPIView.as_view()),
    path("activity", ActivityFeedListAPIView.as_view()),
    path("activity/", ActivityFeedListAPIView.as_view()),
    path("suggestions", SmartSuggestionsAPIView.as_view()),
    path("suggestions/", SmartSuggestionsAPIView.as_view()),
]

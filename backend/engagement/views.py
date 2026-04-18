from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActivityFeed, UserBadge
from .serializers import (
    ActivityFeedSerializer,
    EngagementOverviewSerializer,
    SuggestionSerializer,
    UserBadgeSerializer,
    UserProfileSerializer,
)
from .utils import build_suggestions, get_or_create_profile


class EngagementOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        badges = UserBadge.objects.filter(user=request.user).select_related("badge")
        serializer = EngagementOverviewSerializer(
            {
                "user": request.user,
                "profile": profile,
                "badges": badges,
            }
        )
        return Response(serializer.data)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(UserProfileSerializer(profile).data)


class BadgeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user).select_related("badge")
        return Response(UserBadgeSerializer(badges, many=True).data)


class ActivityFeedListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = ActivityFeed.objects.filter(actor=request.user)[:50]
        return Response(ActivityFeedSerializer(entries, many=True).data)


class SmartSuggestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suggestions = build_suggestions(request.user)
        return Response(SuggestionSerializer(suggestions, many=True).data)

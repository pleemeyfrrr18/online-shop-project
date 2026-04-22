from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    FriendRequestSerializer,
    CreateFriendRequestSerializer,
    FriendshipSerializer,
)
from engagement.serializers import UserProfileSerializer
from engagement.utils import get_or_create_profile
from django.contrib.auth.models import User
from .models import FriendRequest, Friendship


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    return Response(
        {"message": "Logout successful on client side."},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def profile_view(request):
    profile = get_or_create_profile(request.user)
    return Response(
        {
            **UserSerializer(request.user).data,
            "profile": UserProfileSerializer(profile).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def users_list_view(request):
    users = User.objects.filter(is_active=True).exclude(pk=request.user.pk).order_by("username")
    return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)


@api_view(["GET"])
def friends_view(request):
    friendships = Friendship.objects.filter(
        Q(user_one=request.user) | Q(user_two=request.user)
    ).select_related("user_one", "user_two").order_by("-created_at")
    return Response(
        FriendshipSerializer(friendships, many=True, context={"request": request}).data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
def friend_requests_view(request):
    if request.method == "GET":
        received = FriendRequest.objects.filter(
            to_user=request.user,
            status="pending",
        ).select_related("from_user", "to_user").order_by("-created_at")
        sent = FriendRequest.objects.filter(
            from_user=request.user,
        ).select_related("from_user", "to_user").order_by("-created_at")
        updates = sent.exclude(status="pending").order_by("-responded_at", "-created_at")

        return Response(
            {
                "received": FriendRequestSerializer(received, many=True).data,
                "sent": FriendRequestSerializer(sent, many=True).data,
                "updates": FriendRequestSerializer(updates, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

    serializer = CreateFriendRequestSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    friend_request = serializer.save(from_user=request.user)
    return Response(
        FriendRequestSerializer(friend_request).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def friend_request_action_view(request, request_id):
    action = request.data.get("action")
    if action not in ["accept", "decline"]:
        return Response(
            {"detail": "Invalid action. Must be 'accept' or 'decline'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        friend_request = FriendRequest.objects.select_related("from_user", "to_user").get(
            id=request_id,
            to_user=request.user,
        )
    except FriendRequest.DoesNotExist:
        return Response(
            {"detail": "Friend request not found or access denied."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if friend_request.status != "pending":
        return Response(
            {"detail": "This friend request has already been processed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        if action == "accept":
            first_user_id, second_user_id = sorted([friend_request.from_user_id, friend_request.to_user_id])
            Friendship.objects.get_or_create(
                user_one_id=first_user_id,
                user_two_id=second_user_id,
            )
            friend_request.status = "accepted"
            message = f"You are now friends with {friend_request.from_user.username}."
        else:
            friend_request.status = "declined"
            message = f"You declined {friend_request.from_user.username}'s friend request."

        friend_request.responded_at = timezone.now()
        friend_request.save(update_fields=["status", "responded_at"])

    return Response(
        {
            "detail": message,
            "request": FriendRequestSerializer(friend_request).data,
        },
        status=status.HTTP_200_OK,
    )

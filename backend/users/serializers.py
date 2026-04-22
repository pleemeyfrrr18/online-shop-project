from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import models

from .models import FriendRequest, Friendship


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'],
                                        email=validated_data.get('email', ''))
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'),
                            password=attrs.get('password'))
        
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        attrs['user'] = user
        return attrs
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user_username = serializers.CharField(source="from_user.username", read_only=True)
    to_user_username = serializers.CharField(source="to_user.username", read_only=True)

    class Meta:
        model = FriendRequest
        fields = [
            "id",
            "from_user",
            "from_user_username",
            "to_user",
            "to_user_username",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = ["from_user", "status", "created_at", "responded_at"]


class CreateFriendRequestSerializer(serializers.ModelSerializer):
    to_username = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = FriendRequest
        fields = ["to_user", "to_username"]
        extra_kwargs = {
            "to_user": {"required": False},
        }

    def validate(self, attrs):
        from_user = self.context["request"].user
        to_user = attrs.get("to_user")
        to_username = attrs.pop("to_username", None)

        if to_user is None and to_username:
            try:
                to_user = User.objects.get(username__iexact=to_username.strip())
            except User.DoesNotExist:
                raise serializers.ValidationError({"to_username": "No user was found with this username."})
            attrs["to_user"] = to_user

        if to_user is None:
            raise serializers.ValidationError({"to_user": "Choose a user to add as a friend."})

        if to_user == from_user:
            raise serializers.ValidationError({"detail": "You cannot send a friend request to yourself."})

        first_user_id, second_user_id = sorted([from_user.id, to_user.id])
        if Friendship.objects.filter(user_one_id=first_user_id, user_two_id=second_user_id).exists():
            raise serializers.ValidationError({"detail": "You are already friends with this user."})

        existing_request = FriendRequest.objects.filter(
            models.Q(from_user=from_user, to_user=to_user) |
            models.Q(from_user=to_user, to_user=from_user),
            status="pending",
        ).exists()
        if existing_request:
            raise serializers.ValidationError({"detail": "A pending friend request already exists with this user."})

        previous_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists()
        if previous_request:
            raise serializers.ValidationError({"detail": "You have already sent a friend request to this user."})

        return attrs


class FriendshipSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ["id", "friend", "created_at"]

    def get_friend(self, obj):
        request = self.context.get("request")
        current_user = request.user if request else None
        friend = obj.user_two if current_user == obj.user_one else obj.user_one
        return UserSerializer(friend).data


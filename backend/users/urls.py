from django.urls import path
from .views import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    users_list_view,
    friends_view,
    friend_requests_view,
    friend_request_action_view,
)

urlpatterns = [
    path("register", register_view),
    path("register/", register_view),
    path("login", login_view),
    path("login/", login_view),
    path("logout", logout_view),
    path("logout/", logout_view),
    path("me", profile_view),
    path("me/", profile_view),
    path("users", users_list_view),
    path("users/", users_list_view),
    path("friends", friends_view),
    path("friends/", friends_view),
    path("friend-requests", friend_requests_view),
    path("friend-requests/", friend_requests_view),
    path("friend-requests/<int:request_id>/action", friend_request_action_view),
    path("friend-requests/<int:request_id>/action/", friend_request_action_view),
]

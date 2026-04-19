from django.urls import path
from .views import register_view, login_view, logout_view, profile_view

urlpatterns = [
    path("register", register_view),
    path("register/", register_view),
    path("login", login_view),
    path("login/", login_view),
    path("logout", logout_view),
    path("logout/", logout_view),
    path("me", profile_view),
    path("me/", profile_view),
]

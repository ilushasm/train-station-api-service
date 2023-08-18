from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from user.views import (
    CreateUserView,
    ProfileUserView
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register", ),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path("profile/", ProfileUserView.as_view(), name="profile"),
]

app_name = "user"

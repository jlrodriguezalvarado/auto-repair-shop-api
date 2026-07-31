from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from apps.users.views.api import UserViewSet
from apps.users.views.auth import CustomTokenObtainPairView, CustomTokenRefreshView
from apps.users.views.password import ChangePasswordView
=======
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.users.views.api import UserViewSet, CurrentUserView
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
<<<<<<< HEAD
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
=======
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", CurrentUserView.as_view(), name="current_user"),
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211
    path("", include(router.urls)),
]

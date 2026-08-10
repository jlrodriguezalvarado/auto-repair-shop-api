from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views.api import UserViewSet
from apps.users.views.auth import CustomTokenObtainPairView, CustomTokenRefreshView
from apps.users.views.password import ChangePasswordView

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("", include(router.urls)),
]

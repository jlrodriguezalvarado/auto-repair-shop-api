from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from apps.company.models import Company
from apps.users.serializers.api import UserSerializer

User = get_user_model()

def assert_user_may_authenticate(user):
    if user is None:
        raise exceptions.AuthenticationFailed("No active account found with the given credentials.")
    if user.deleted_at is not None:
        raise exceptions.AuthenticationFailed(
            "This account has been deleted.",
            code="user_deleted",
        )
    if user.company_id:
        company = Company.all_objects.filter(pk=user.company_id).first()
        if company is None or company.deleted_at is not None:
            raise exceptions.AuthenticationFailed(
                "Your company is unavailable.",
                code="company_deleted",
            )

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        alive = User.objects.filter(**{self.username_field: username}).first()
        if alive is not None:
            assert_user_may_authenticate(alive)
        else:
            deleted = User.all_objects.filter(
                **{self.username_field: username},
                deleted_at__isnull=False,
            ).first()
            if deleted is not None:
                assert_user_may_authenticate(deleted)
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.get(api_settings.USER_ID_CLAIM)
        user = User.all_objects.filter(**{api_settings.USER_ID_FIELD: user_id}).first()
        assert_user_may_authenticate(user)
        return super().validate(attrs)

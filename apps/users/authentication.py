from datetime import datetime, timezone as dt_timezone
from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

class UserAwareJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as exc:
            raise exceptions.AuthenticationFailed(
                "Token contained no recognizable user identification",
                code="token_not_valid",
            ) from exc
        try:
            user = User.all_objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("User not found", code="user_not_found") from exc
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive", code="user_inactive")
        if user.deleted_at is not None:
            raise exceptions.AuthenticationFailed(
                "This account has been deleted.",
                code="user_deleted",
            )
        company_id = getattr(user, "company_id", None)
        if company_id:
            from apps.company.models import Company
            company = Company.all_objects.filter(pk=company_id).first()
            if company is None or company.deleted_at is not None:
                raise exceptions.AuthenticationFailed(
                    "Your company is unavailable.",
                    code="company_deleted",
                )
        invalid_before = getattr(user, "tokens_invalid_before", None)
        token_iat = validated_token.get("iat")
        if invalid_before and token_iat:
            issued_at = datetime.fromtimestamp(token_iat, tz=dt_timezone.utc)
            if issued_at <= invalid_before:
                raise exceptions.AuthenticationFailed(
                    "Token has been revoked.",
                    code="token_revoked",
                )
        return user

class UserAwareJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.users.authentication.UserAwareJWTAuthentication"
    name = "BearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }

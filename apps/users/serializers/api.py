from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from apps.company.serializers.api import CompanyBriefSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    company = CompanyBriefSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "company",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "company", "created_at", "updated_at", "deleted_at")

    def validate_role(self, value):
        if value == User.Role.SUPER_ADMIN:
            raise serializers.ValidationError("Cannot assign SUPER_ADMIN role.")
        return value

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "first_name", "last_name", "role")

    def validate_role(self, value):
        if value == User.Role.SUPER_ADMIN:
            raise serializers.ValidationError("Cannot assign SUPER_ADMIN role.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        company = getattr(request.user, "company", None) if request else None
        if company is None:
            raise serializers.ValidationError({"company": "Authenticated tenant user required."})
        validated_data["company"] = company
        return User.objects.create_user(**validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match.",
            })
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": "New password must be different from current password.",
            })
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.tokens_invalid_before = timezone.now()
        user.save(update_fields=["password", "tokens_invalid_before"])
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        return user

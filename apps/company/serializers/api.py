from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from apps.company.models import Company

User = get_user_model()

class CompanyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name")

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "tax_id",
            "address",
            "phone",
            "secondary_phone",
            "email",
            "logo",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")

class CompanyAdminUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")

class CompanyCreateSerializer(serializers.ModelSerializer):
    admin_user = CompanyAdminUserSerializer(write_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "tax_id",
            "address",
            "phone",
            "secondary_phone",
            "email",
            "logo",
            "admin_user",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")

    def validate_admin_user(self, value):
        username = value["username"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "A user with that username already exists."})
        email = value["email"]
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        return value

    @transaction.atomic
    def create(self, validated_data):
        admin_data = validated_data.pop("admin_user")
        company = Company.objects.create(**validated_data)
        User.objects.create_user(
            username=admin_data["username"],
            email=admin_data["email"],
            password=admin_data["password"],
            first_name=admin_data.get("first_name", ""),
            last_name=admin_data.get("last_name", ""),
            role=User.Role.ADMINISTRATOR,
            company=company,
        )
        return company

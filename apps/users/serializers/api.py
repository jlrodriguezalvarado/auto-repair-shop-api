from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "first_name", "last_name", "role")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

from rest_framework import serializers
from apps.notifications.models import Notification, PushSubscription
from apps.notifications.services.push_notification_service import PushNotificationService

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "body",
            "data",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = fields

class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = (
            "id",
            "endpoint",
            "user_agent",
            "platform",
            "is_active",
            "last_used_at",
            "created_at",
            "deleted_at",
        )
        read_only_fields = fields

class PushSubscriptionWriteSerializer(serializers.Serializer):
    endpoint = serializers.CharField()
    keys = serializers.DictField(child=serializers.CharField())
    user_agent = serializers.CharField(required=False, allow_blank=True)
    platform = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def create(self, validated_data):
        request = self.context["request"]
        return PushNotificationService.save_subscription(
            user=request.user,
            payload=validated_data,
            user_agent=validated_data.get("user_agent", ""),
            platform=validated_data.get("platform", ""),
        )

class PushUnsubscribeSerializer(serializers.Serializer):
    endpoint = serializers.CharField()

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.notifications.models import Notification, PushSubscription
from apps.notifications.serializers import (
    NotificationSerializer,
    PushSubscriptionSerializer,
    PushSubscriptionWriteSerializer,
    PushUnsubscribeSerializer,
)
from apps.notifications.services.notification_service import NotificationService
from apps.notifications.services.push_notification_service import PushNotificationService

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.all_objects.none()
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        queryset = Notification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            normalized = is_read.strip().lower()
            if normalized in ("true", "1"):
                queryset = queryset.filter(is_read=True)
            elif normalized in ("false", "0"):
                queryset = queryset.filter(is_read=False)
        notification_type = self.request.query_params.get("notification_type")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        return queryset

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification = NotificationService.mark_as_read(notification, request.user)
        return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        updated_count = NotificationService.mark_all_as_read(request.user)
        return Response({"updated_count": updated_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})

@soft_delete_schema_view()
class PushSubscriptionViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = PushSubscription.all_objects.none()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.queryset
        qs = PushSubscription.all_objects.filter(user=self.request.user)
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def get_serializer_class(self):
        if self.action == "create":
            return PushSubscriptionWriteSerializer
        return PushSubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(PushSubscriptionSerializer(instance).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request):
        serializer = PushUnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        endpoint = serializer.validated_data["endpoint"]
        PushNotificationService.deactivate_subscription(request.user, endpoint)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="vapid-public-key")
    def vapid_public_key(self, request):
        public_key = settings.WEB_PUSH_VAPID_PUBLIC_KEY
        if not public_key:
            raise NotFound("VAPID public key is not configured.")
        return Response({"public_key": public_key})

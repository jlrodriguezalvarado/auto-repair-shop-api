from django.utils import timezone
from apps.notifications.models import Notification
from apps.notifications.services.push_notification_service import PushNotificationService

class NotificationService:
    @staticmethod
    def create_and_notify(
        *,
        user,
        notification_type,
        title,
        body="",
        data=None,
        send_push=True,
    ):
        payload_data = data or {}
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            body=body,
            data=payload_data,
        )
        if send_push:
            push_payload = PushNotificationService.build_payload(
                title=title,
                body=body,
                url=payload_data.get("url", "/"),
                notification_type=notification_type,
                extra={k: v for k, v in payload_data.items() if k != "url"},
            )
            PushNotificationService.send_to_user(user, push_payload)
        return notification

    @staticmethod
    def mark_as_read(notification, user):
        if notification.user_id != user.id:
            raise PermissionError("Notification does not belong to this user.")
        if notification.is_read:
            return notification
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return notification

    @staticmethod
    def mark_all_as_read(user):
        now = timezone.now()
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=now,
            updated_at=now,
        )

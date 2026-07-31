import json
import logging
import os
from django.conf import settings
from django.utils import timezone
from py_vapid import Vapid
from pywebpush import WebPushException, webpush
from apps.notifications.models import PushSubscription

logger = logging.getLogger(__name__)

class PushNotificationService:
    @staticmethod
    def save_subscription(user, payload, user_agent="", platform=""):
        endpoint = payload.get("endpoint", "")
        keys = payload.get("keys", {})
        p256dh = keys.get("p256dh", "")
        auth_key = keys.get("auth", "")
        if not endpoint or not p256dh or not auth_key:
            raise ValueError("Invalid push subscription payload.")
        subscription, _created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "user": user,
                "p256dh": p256dh,
                "auth": auth_key,
                "user_agent": user_agent or payload.get("user_agent", ""),
                "platform": platform or payload.get("platform", ""),
                "is_active": True,
                "last_used_at": timezone.now(),
            },
        )
        return subscription

    @staticmethod
    def deactivate_subscription(user, endpoint):
        updated = PushSubscription.objects.filter(
            user=user,
            endpoint=endpoint,
        ).update(is_active=False)
        return updated > 0

    @staticmethod
    def deactivate_by_endpoint(endpoint):
        PushSubscription.objects.filter(endpoint=endpoint).update(is_active=False)

    @staticmethod
    def send_to_user(user, payload):
        if not settings.WEB_PUSH_VAPID_PRIVATE_KEY:
            logger.warning("WEB_PUSH_VAPID_PRIVATE_KEY not configured; skipping push.")
            return
        subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
        for subscription in subscriptions:
            PushNotificationService._send_to_subscription(subscription, payload)

    @staticmethod
    def build_payload(*, title, body="", url="/", notification_type="", extra=None, icon="/icons/icon-192x192.png", badge="/icons/badge-72x72.png"):
        data = {"url": url, "type": notification_type}
        if extra:
            data.update(extra)
        return {
            "notification": {
                "title": title,
                "body": body,
                "icon": icon,
                "badge": badge,
                "data": data,
                "actions": [{"action": "open", "title": "Open"}],
            },
        }

    @staticmethod
    def _resolve_vapid_private_key():
        key = settings.WEB_PUSH_VAPID_PRIVATE_KEY
        if not key:
            return None
        if os.path.isfile(key):
            return key
        if "BEGIN" in key and "PRIVATE KEY" in key:
            return Vapid.from_pem(key.encode("utf-8"))
        return key

    @staticmethod
    def _send_to_subscription(subscription, payload):
        vapid_private_key = PushNotificationService._resolve_vapid_private_key()
        if not vapid_private_key:
            return
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }
        vapid_claims = {"sub": settings.WEB_PUSH_VAPID_SUBJECT}
        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
                ttl=86400,
            )
            subscription.last_used_at = timezone.now()
            subscription.save(update_fields=["last_used_at", "updated_at"])
        except WebPushException as exc:
            status_code = getattr(exc.response, "status_code", None) if exc.response else None
            if status_code in (401, 403, 404, 410):
                subscription.is_active = False
                subscription.save(update_fields=["is_active", "updated_at"])
            logger.warning(
                "Web push failed for subscription %s with status %s: %s",
                subscription.id,
                status_code,
                exc,
            )
        except (ValueError, TypeError, OSError) as exc:
            logger.error(
                "Web push VAPID key configuration error for subscription %s: %s",
                subscription.id,
                exc,
            )

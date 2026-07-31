from django.conf import settings
from django.db import models
from apps.common.models import BaseModel

class PushSubscription(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.TextField()
    p256dh = models.TextField()
    auth = models.TextField()
    user_agent = models.TextField(blank=True)
    platform = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["endpoint"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_push_subscription_endpoint_alive",
            ),
        ]

    def __str__(self):
        return f"PushSubscription {self.id} for {self.user_id}"

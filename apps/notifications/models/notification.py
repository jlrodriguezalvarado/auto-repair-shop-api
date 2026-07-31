from django.conf import settings
from django.db import models
from apps.common.models import BaseModel

class Notification(BaseModel):
    TYPE_WORK_ORDER_STATUS = "work_order.status_changed"
    TYPE_WORK_ORDER_ASSIGNED = "work_order.assigned"
    TYPE_ESTIMATE_APPROVED = "estimate.approved"
    TYPE_ESTIMATE_READY = "estimate.ready"
    TYPE_RECEIPT_ISSUED = "receipt.issued"
    TYPE_ADMIN_TEST = "admin.test_push"
    TYPE_CHOICES = (
        (TYPE_WORK_ORDER_STATUS, "Work order status changed"),
        (TYPE_WORK_ORDER_ASSIGNED, "Work order assigned"),
        (TYPE_ESTIMATE_APPROVED, "Estimate approved"),
        (TYPE_ESTIMATE_READY, "Estimate ready"),
        (TYPE_RECEIPT_ISSUED, "Receipt issued"),
        (TYPE_ADMIN_TEST, "Admin test push"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user_id}"

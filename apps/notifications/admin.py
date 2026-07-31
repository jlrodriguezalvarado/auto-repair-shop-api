from django.contrib import admin
from apps.notifications.models import Notification, PushSubscription

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "body", "user__username", "user__email")

@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "is_active", "last_used_at", "created_at")
    list_filter = ("is_active", "platform")
    search_fields = ("endpoint", "user__username", "user__email")

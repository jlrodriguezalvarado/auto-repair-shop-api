from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from apps.notifications.models import PushSubscription
from apps.notifications.services.push_notification_service import PushNotificationService
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "company", "is_active", "is_staff")
    search_fields = ("username", "email")
    list_filter = ("role", "company", "is_active", "is_staff")
    autocomplete_fields = ("company",)
    readonly_fields = ("push_notifications_section",)
    actions = ("send_test_push_notification",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:user_id>/send-test-push/",
                self.admin_site.admin_view(self.send_test_push_view),
                name="users_user_send_test_push",
            ),
        ]
        return custom_urls + urls

    def push_notifications_section(self, obj):
        if not obj or not obj.pk:
            return "Save the user to manage push notifications."
        subscriptions = PushSubscription.objects.filter(user=obj).order_by("-is_active", "-last_used_at")
        active_count = subscriptions.filter(is_active=True).count()
        if not subscriptions.exists():
            return "No push subscriptions for this user."
        send_url = reverse("admin:users_user_send_test_push", args=[obj.pk])
        rows = []
        for subscription in subscriptions:
            status_label = "active" if subscription.is_active else "inactive"
            endpoint_preview = subscription.endpoint
            if len(endpoint_preview) > 72:
                endpoint_preview = endpoint_preview[:69] + "..."
            rows.append(
                (
                    status_label,
                    subscription.platform or "—",
                    subscription.last_used_at or "never",
                    endpoint_preview,
                )
            )
        subscriptions_html = format_html(
            "<ul>{}</ul>",
            format_html_join(
                "",
                (
                    "<li><strong>{}</strong> · platform: {} · last used: {}"
                    "<br><code>{}</code></li>"
                ),
                rows,
            ),
        )
        return format_html(
            "<p>Active subscriptions: <strong>{}</strong></p>{}{}",
            active_count,
            subscriptions_html,
            format_html(
                '<p><a class="button" href="{}">Send test push notification</a></p>',
                send_url,
            )
            if active_count
            else format_html("<p>No active subscriptions to test.</p>"),
        )

    push_notifications_section.short_description = "Push notifications"

    @staticmethod
    def _build_test_push_payload():
        return PushNotificationService.build_payload(
            title="Test push notification",
            body="This is a test push sent from Django admin.",
            url="/dashboard",
            notification_type="admin.test_push",
        )

    def _send_test_push_to_user(self, request, user):
        if not settings.WEB_PUSH_VAPID_PRIVATE_KEY:
            self.message_user(
                request,
                "WEB_PUSH_VAPID_PRIVATE_KEY is not configured; push was skipped.",
                level=messages.WARNING,
            )
            return False
        active_count = PushSubscription.objects.filter(user=user, is_active=True).count()
        if active_count == 0:
            self.message_user(
                request,
                f"No active push subscriptions for {user.username}.",
                level=messages.WARNING,
            )
            return False
        try:
            PushNotificationService.send_to_user(user, self._build_test_push_payload())
        except Exception as exc:
            self.message_user(
                request,
                f"Failed to send test push to {user.username}: {exc}",
                level=messages.ERROR,
            )
            return False
        self.message_user(
            request,
            f"Test push notification sent to {user.username} ({active_count} subscription(s)).",
            level=messages.SUCCESS,
        )
        return True

    def send_test_push_view(self, request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            self.message_user(request, "User not found.", level=messages.ERROR)
            return HttpResponseRedirect(reverse("admin:users_user_changelist"))
        self._send_test_push_to_user(request, user)
        return HttpResponseRedirect(reverse("admin:users_user_change", args=[user_id]))

    @admin.action(description="Send test push notification")
    def send_test_push_notification(self, request, queryset):
        for user in queryset:
            self._send_test_push_to_user(request, user)

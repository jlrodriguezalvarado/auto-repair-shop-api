from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.notifications.views import NotificationViewSet, PushSubscriptionViewSet

router = DefaultRouter()
router.register("push-subscriptions", PushSubscriptionViewSet, basename="push-subscription")
router.register("", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.customers.views.api import CustomerProfileViewSet

app_name = "customers"

router = DefaultRouter()
router.register(r"profiles", CustomerProfileViewSet, basename="customer-profile")

urlpatterns = [
    path("", include(router.urls)),
]

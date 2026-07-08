from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.vehicles.views.api import VehicleViewSet

app_name = "vehicles"

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")

urlpatterns = [
    path("", include(router.urls)),
]

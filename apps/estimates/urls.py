from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.estimates.views.api import EstimateViewSet, EstimateServiceViewSet, EstimateItemViewSet

app_name = "estimates"

router = DefaultRouter()
router.register(r"estimates", EstimateViewSet, basename="estimate")
router.register(r"estimate-services", EstimateServiceViewSet, basename="estimate-service")
router.register(r"estimate-items", EstimateItemViewSet, basename="estimate-item")

urlpatterns = [
    path("", include(router.urls)),
]

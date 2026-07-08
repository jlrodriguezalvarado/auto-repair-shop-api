from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.catalog.views.api import ServiceCatalogViewSet

app_name = "catalog"

router = DefaultRouter()
router.register(r"services", ServiceCatalogViewSet, basename="service-catalog")

urlpatterns = [
    path("", include(router.urls)),
]

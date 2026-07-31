from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.company.views.api import CompanyViewSet

app_name = "companies"

router = DefaultRouter()
router.register(r"", CompanyViewSet, basename="companies")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.receipts.views.api import ReceiptViewSet, ReceiptServiceViewSet, ReceiptItemViewSet

app_name = "receipts"

router = DefaultRouter()
router.register(r"receipts", ReceiptViewSet, basename="receipt")
router.register(r"receipt-services", ReceiptServiceViewSet, basename="receipt-service")
router.register(r"receipt-items", ReceiptItemViewSet, basename="receipt-item")

urlpatterns = [
    path("", include(router.urls)),
]

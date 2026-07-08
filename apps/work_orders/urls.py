from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.work_orders.views.api import WorkOrderViewSet, WorkOrderServiceViewSet, WorkOrderItemViewSet

app_name = "work_orders"

router = DefaultRouter()
router.register(r"orders", WorkOrderViewSet, basename="work-order")
router.register(r"order-services", WorkOrderServiceViewSet, basename="work-order-service")
router.register(r"order-items", WorkOrderItemViewSet, basename="work-order-item")

urlpatterns = [
    path("", include(router.urls)),
]

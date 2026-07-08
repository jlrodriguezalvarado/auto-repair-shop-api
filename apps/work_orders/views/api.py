from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from apps.work_orders.serializers.api import (
    WorkOrderSerializer,
    WorkOrderCreateUpdateSerializer,
    WorkOrderServiceSerializer,
    WorkOrderItemSerializer
)
from apps.work_orders.services import add_service_to_work_order
from apps.users.permissions import IsAdministrator, IsSecretary, IsMechanic, IsCustomer

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().prefetch_related("services", "items")
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["customer", "vehicle", "assigned_mechanic", "status"]
    search_fields = ["code", "vehicle__plate", "customer__first_name", "customer__last_name"]
    ordering_fields = ["created_at", "status", "code"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return WorkOrderCreateUpdateSerializer
        return WorkOrderSerializer

    def get_permissions(self):
        if not self.request.user.is_authenticated:
            return [permissions.IsAuthenticated()]
        if self.request.user.role == "MECHANIC":
            return [IsMechanic()]
        if self.request.user.role == "CUSTOMER":
            return [IsCustomer()]
        return [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if user.role == "MECHANIC":
            return queryset.filter(assigned_mechanic=user)
        if user.role == "CUSTOMER":
            if hasattr(user, 'customer_profile'):
                return queryset.filter(customer=user.customer_profile)
            return queryset.none()
        return queryset

    @action(detail=True, methods=["post"])
    def assign_mechanic(self, request, pk=None):
        work_order = self.get_object()
        mechanic_id = request.data.get("mechanic_id")
        if not mechanic_id:
            return Response({"detail": "mechanic_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        work_order.assigned_mechanic_id = mechanic_id
        work_order.save()
        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        work_order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in WorkOrder.Status.values:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        work_order.status = new_status
        work_order.save()
        return Response(WorkOrderSerializer(work_order).data)


class WorkOrderServiceViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderService.objects.all()
    serializer_class = WorkOrderServiceSerializer
    permission_classes = [IsAdministrator | IsSecretary]

    def perform_create(self, serializer):
        service = serializer.validated_data['service']
        serializer.save(
            name_snapshot=service.name,
            description_snapshot=service.description,
            unit_price=serializer.validated_data.get('unit_price', service.base_price)
        )


class WorkOrderItemViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderItem.objects.all()
    serializer_class = WorkOrderItemSerializer
    permission_classes = [IsAdministrator | IsSecretary]

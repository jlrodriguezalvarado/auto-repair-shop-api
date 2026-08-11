from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import (
    TenantQuerysetMixin,
    require_tenant_access,
    resolve_company_id,
    require_tenant_user,
    assert_same_company,
)
from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from apps.work_orders.serializers.api import (
    WorkOrderSerializer,
    WorkOrderCreateUpdateSerializer,
    WorkOrderServiceSerializer,
    WorkOrderItemSerializer
)
from apps.users.permissions import IsAdministrator, IsSecretary, IsMechanic, IsCustomer, IsTenantUser

User = get_user_model()

@soft_delete_schema_view()
class WorkOrderViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = WorkOrder.all_objects.all().prefetch_related("services", "items")
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
        base = [IsTenantUser()]
        if self.action == "hard_delete":
            return base + [IsAdministrator()]
        if self.action in ["list", "retrieve"]:
            return base + [(IsAdministrator | IsSecretary | IsMechanic | IsCustomer)()]
        if self.action == "change_status":
            return base + [(IsAdministrator | IsSecretary | IsMechanic)()]
        # create/update/destroy/assign_mechanic/restore: staff only
        return base + [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        queryset = WorkOrder.all_objects.filter(
            company_id=resolve_company_id(self.request)
        ).prefetch_related("services", "items")
        user = self.request.user
        if user.role == "MECHANIC":
            queryset = queryset.filter(assigned_mechanic=user)
        elif user.role == "CUSTOMER":
            if hasattr(user, "customer_profile"):
                queryset = queryset.filter(customer=user.customer_profile)
            else:
                queryset = queryset.none()
        if self.action == "restore":
            return queryset.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return queryset
        return self.apply_deleted_filter(queryset)

    @action(detail=True, methods=["post"])
    def assign_mechanic(self, request, pk=None):
        work_order = self.get_object()
        mechanic_id = request.data.get("mechanic_id")
        if not mechanic_id:
            return Response({"detail": "mechanic_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mechanic = User.objects.get(pk=mechanic_id)
        except (User.DoesNotExist, TypeError, ValueError):
            return Response({"detail": "Mechanic not found"}, status=status.HTTP_400_BAD_REQUEST)
        if mechanic.role != User.Role.MECHANIC:
            return Response({"detail": "User is not a mechanic"}, status=status.HTTP_400_BAD_REQUEST)
        if mechanic.company_id != work_order.company_id:
            return Response(
                {"detail": "Mechanic belongs to another company"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        work_order.assigned_mechanic = mechanic
        work_order.save()
        from apps.notifications.services.domain_events import notify_work_order_assigned
        notify_work_order_assigned(work_order, actor=request.user)
        return Response(WorkOrderSerializer(work_order).data)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        work_order = self.get_object()
        new_status = request.data.get("status")
        if new_status not in WorkOrder.Status.values:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        work_order.status = new_status
        work_order.save()
        from apps.notifications.services.domain_events import notify_work_order_status_changed
        notify_work_order_status_changed(work_order, actor=request.user)
        return Response(WorkOrderSerializer(work_order).data)

@soft_delete_schema_view()
class WorkOrderServiceViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = WorkOrderService.all_objects.all()
    serializer_class = WorkOrderServiceSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = WorkOrderService.all_objects.filter(
            work_order__company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        work_order = serializer.validated_data["work_order"]
        assert_same_company(work_order, self.request.user.company_id, field_name="work_order")
        service = serializer.validated_data.get("service")
        assert_same_company(service, self.request.user.company_id, field_name="service")
        serializer.save(
            name_snapshot=service.name,
            description_snapshot=service.description,
            unit_price=serializer.validated_data.get("unit_price", service.base_price)
        )

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        instance.delete()

@soft_delete_schema_view()
class WorkOrderItemViewSet(SoftDeleteViewSetMixin, viewsets.ModelViewSet):
    queryset = WorkOrderItem.all_objects.all()
    serializer_class = WorkOrderItemSerializer

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        qs = WorkOrderItem.all_objects.filter(
            work_order__company_id=resolve_company_id(self.request)
        )
        if self.action == "restore":
            return qs.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return qs
        return self.apply_deleted_filter(qs)

    def perform_create(self, serializer):
        require_tenant_user(self.request.user)
        work_order = serializer.validated_data["work_order"]
        assert_same_company(work_order, self.request.user.company_id, field_name="work_order")
        serializer.save()

    def perform_destroy(self, instance):
        require_tenant_user(self.request.user)
        instance.delete()

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import TenantQuerysetMixin, require_tenant_access, resolve_company_id
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers.api import VehicleSerializer
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer, IsTenantUser

@soft_delete_schema_view()
class VehicleViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Vehicle.all_objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["customer", "is_active", "plate"]
    search_fields = ["plate", "brand", "model", "vin"]
    ordering_fields = ["created_at", "plate", "year"]

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        if self.action in ["list", "retrieve"]:
            return [IsTenantUser(), (IsAdministrator | IsSecretary | IsCustomer)()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        require_tenant_access(self.request, write=False)
        queryset = Vehicle.all_objects.filter(company_id=resolve_company_id(self.request))
        if self.request.user.role == "CUSTOMER":
            if hasattr(self.request.user, "customer_profile"):
                queryset = queryset.filter(customer=self.request.user.customer_profile)
            else:
                queryset = queryset.none()
        if self.action == "restore":
            return queryset.filter(deleted_at__isnull=False)
        if self.action == "hard_delete":
            return queryset
        return self.apply_deleted_filter(queryset)

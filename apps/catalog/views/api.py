from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.common.soft_delete import SoftDeleteViewSetMixin, soft_delete_schema_view
from apps.common.tenancy import TenantQuerysetMixin
from apps.catalog.models import ServiceCatalog
from apps.catalog.serializers.api import ServiceCatalogSerializer
from apps.users.permissions import IsAdministrator, IsSecretary, IsTenantUser

@soft_delete_schema_view()
class ServiceCatalogViewSet(SoftDeleteViewSetMixin, TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = ServiceCatalog.all_objects.all()
    serializer_class = ServiceCatalogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name", "base_price"]

    def get_permissions(self):
        if self.action == "hard_delete":
            return [IsTenantUser(), IsAdministrator()]
        if self.action in ["list", "retrieve"]:
            return [IsTenantUser()]
        return [IsTenantUser(), (IsAdministrator | IsSecretary)()]

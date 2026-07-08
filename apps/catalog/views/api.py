from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.catalog.models import ServiceCatalog
from apps.catalog.serializers.api import ServiceCatalogSerializer
from apps.users.permissions import IsAdministrator, IsSecretary

class ServiceCatalogViewSet(viewsets.ModelViewSet):
    queryset = ServiceCatalog.objects.all()
    serializer_class = ServiceCatalogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name", "base_price"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [(IsAdministrator | IsSecretary)()]

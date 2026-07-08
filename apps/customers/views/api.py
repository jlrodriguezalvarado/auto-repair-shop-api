from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.customers.models import CustomerProfile
from apps.customers.serializers.api import CustomerProfileSerializer
from apps.users.permissions import IsAdministrator, IsSecretary

class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["first_name", "last_name", "phone", "email", "document_id"]
    ordering_fields = ["created_at", "first_name", "last_name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "update", "partial_update"]:
            return [(IsAdministrator | IsSecretary)()]
        return [IsAdministrator()]

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers.api import VehicleSerializer
from apps.users.permissions import IsAdministrator, IsSecretary, IsCustomer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["customer", "is_active", "plate"]
    search_fields = ["plate", "brand", "model", "vin"]
    ordering_fields = ["created_at", "plate", "year"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [(IsAdministrator | IsSecretary | IsCustomer)()]
        return [(IsAdministrator | IsSecretary)()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == "CUSTOMER":
            # If user has a profile, filter by it
            if hasattr(self.request.user, 'customer_profile'):
                return queryset.filter(customer=self.request.user.customer_profile)
            return queryset.none()
        return queryset

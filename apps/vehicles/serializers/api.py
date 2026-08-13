from rest_framework import serializers
from apps.common.tenancy import TenantForeignKeyValidatorMixin
from apps.vehicles.models import Vehicle

class VehicleSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("customer",)

    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("company", "deleted_at")

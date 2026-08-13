from rest_framework import serializers
from apps.common.tenancy import TenantForeignKeyValidatorMixin
from apps.estimates.models import Estimate, EstimateService, EstimateItem

class EstimateServiceSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("estimate", "service")

    class Meta:
        model = EstimateService
        fields = "__all__"
        read_only_fields = ("total_price", "name_snapshot", "description_snapshot", "deleted_at")

class EstimateItemSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("estimate",)

    class Meta:
        model = EstimateItem
        fields = "__all__"
        read_only_fields = ("total_cost", "deleted_at")

class EstimateSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("customer", "vehicle", "work_order")
    services = EstimateServiceSerializer(many=True, read_only=True)
    items = EstimateItemSerializer(many=True, read_only=True)

    class Meta:
        model = Estimate
        fields = "__all__"
        read_only_fields = ("code", "company", "created_at", "updated_at", "deleted_at", "subtotal", "tax_amount", "total")

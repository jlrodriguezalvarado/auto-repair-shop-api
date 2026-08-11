from rest_framework import serializers
from apps.common.tenancy import TenantForeignKeyValidatorMixin
from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from apps.work_orders.services import get_work_order_totals

class WorkOrderServiceSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("work_order", "service")

    class Meta:
        model = WorkOrderService
        fields = "__all__"
        read_only_fields = ("total_price", "name_snapshot", "description_snapshot", "deleted_at")

class WorkOrderItemSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("work_order",)

    class Meta:
        model = WorkOrderItem
        fields = "__all__"
        read_only_fields = ("total_cost", "deleted_at")

class WorkOrderSerializer(serializers.ModelSerializer):
    totals = serializers.SerializerMethodField()
    services = WorkOrderServiceSerializer(many=True, read_only=True)
    items = WorkOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ("code", "company", "created_at", "updated_at", "deleted_at")

    def get_totals(self, obj):
        return get_work_order_totals(obj)

class WorkOrderCreateUpdateSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("customer", "vehicle", "assigned_mechanic")

    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ("code", "company", "created_at", "updated_at", "deleted_at")

    def validate_assigned_mechanic(self, value):
        if value is None:
            return value
        if getattr(value, "role", None) != "MECHANIC":
            raise serializers.ValidationError("assigned_mechanic must have MECHANIC role.")
        return value

from rest_framework import serializers
from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from apps.work_orders.services import get_work_order_totals

class WorkOrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderService
        fields = "__all__"
        read_only_fields = ("total_price", "name_snapshot", "description_snapshot")

class WorkOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderItem
        fields = "__all__"
        read_only_fields = ("total_cost",)

class WorkOrderSerializer(serializers.ModelSerializer):
    totals = serializers.SerializerMethodField()
    services = WorkOrderServiceSerializer(many=True, read_only=True)
    items = WorkOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ("code", "created_at", "updated_at")

    def get_totals(self, obj):
        return get_work_order_totals(obj)

class WorkOrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = "__all__"
        read_only_fields = ("code", "created_at", "updated_at")

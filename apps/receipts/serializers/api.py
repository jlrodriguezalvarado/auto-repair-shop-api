from rest_framework import serializers
from apps.common.tenancy import TenantForeignKeyValidatorMixin
from apps.receipts.models import Receipt, ReceiptService, ReceiptItem, ReceiptPayment

class ReceiptServiceSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("receipt", "service")

    class Meta:
        model = ReceiptService
        fields = "__all__"
        read_only_fields = ("total_price", "name_snapshot", "description_snapshot", "deleted_at")

class ReceiptItemSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("receipt",)

    class Meta:
        model = ReceiptItem
        fields = "__all__"
        read_only_fields = ("total_cost", "deleted_at")

class ReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptPayment
        fields = "__all__"
        read_only_fields = ("payment_date", "deleted_at")

class ReceiptSerializer(TenantForeignKeyValidatorMixin, serializers.ModelSerializer):
    tenant_fk_fields = ("customer", "vehicle", "work_order", "estimate")
    services = ReceiptServiceSerializer(many=True, read_only=True)
    items = ReceiptItemSerializer(many=True, read_only=True)
    payments = ReceiptPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"
        read_only_fields = ("code", "company", "created_at", "updated_at", "deleted_at", "subtotal", "tax_amount", "total", "paid_amount", "pending_amount", "issued_at")

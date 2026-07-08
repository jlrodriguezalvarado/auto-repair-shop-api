from rest_framework import serializers
from apps.receipts.models import Receipt, ReceiptService, ReceiptItem, ReceiptPayment

class ReceiptServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptService
        fields = "__all__"
        read_only_fields = ("total_price", "name_snapshot", "description_snapshot")

class ReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptItem
        fields = "__all__"
        read_only_fields = ("total_cost",)

class ReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptPayment
        fields = "__all__"
        read_only_fields = ("payment_date",)

class ReceiptSerializer(serializers.ModelSerializer):
    services = ReceiptServiceSerializer(many=True, read_only=True)
    items = ReceiptItemSerializer(many=True, read_only=True)
    payments = ReceiptPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"
        read_only_fields = ("code", "created_at", "updated_at", "subtotal", "tax_amount", "total", "paid_amount", "pending_amount", "issued_at")

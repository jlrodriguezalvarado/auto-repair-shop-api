from django.db import models
from apps.common.models import BaseModel
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.work_orders.models import WorkOrder
from apps.estimates.models import Estimate
from apps.catalog.models import ServiceCatalog
import uuid

class Receipt(BaseModel):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partial"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    code = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="receipts")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="receipts")
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="receipts")
    estimate = models.ForeignKey(Estimate, on_delete=models.SET_NULL, null=True, blank=True, related_name="receipts")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    notes = models.TextField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    pdf_file = models.FileField(upload_to="receipts_pdfs/", blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"REC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"


class ReceiptService(BaseModel):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="services")
    service = models.ForeignKey(ServiceCatalog, on_delete=models.SET_NULL, null=True)
    name_snapshot = models.CharField(max_length=255)
    description_snapshot = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class ReceiptItem(BaseModel):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    provided_by = models.CharField(max_length=20, default="workshop")
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class ReceiptPayment(BaseModel):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        TRANSFER = "transfer", "Transfer"
        MOBILE_PAYMENT = "mobile_payment", "Mobile Payment"
        ZELLE = "zelle", "Zelle"
        OTHER = "other", "Other"

    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

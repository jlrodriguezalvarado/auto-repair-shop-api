from django.db import models
from apps.common.models import BaseModel
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.work_orders.models import WorkOrder
import uuid

class Estimate(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="estimates",
    )
    code = models.CharField(max_length=20, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="estimates")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="estimates")
    work_order = models.OneToOneField(WorkOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="estimate")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    pdf_file = models.FileField(upload_to="estimates_pdfs/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"EST-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_estimate_code_alive",
            ),
        ]


class EstimateService(BaseModel):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="services")
    service = models.ForeignKey(ServiceCatalog, on_delete=models.SET_NULL, null=True)
    name_snapshot = models.CharField(max_length=255)
    description_snapshot = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class EstimateItem(BaseModel):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="items")
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

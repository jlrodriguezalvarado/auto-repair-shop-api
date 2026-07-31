from django.db import models
from django.conf import settings
from apps.common.models import BaseModel
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
import uuid
class WorkOrder(BaseModel):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        UNDER_REVIEW = "under_review", "Under Review"
        ESTIMATED = "estimated", "Estimated"
        APPROVED = "approved", "Approved"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="work_orders",
    )
    code = models.CharField(max_length=20, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="work_orders")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="work_orders")
    assigned_mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_work_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    private_note = models.TextField(blank=True, null=True)
    customer_complaint = models.TextField(blank=True, null=True)
    diagnosis_note = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(deleted_at__isnull=True),
                name="uniq_work_order_code_alive",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"WO-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class WorkOrderService(BaseModel):
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="services")
    service = models.ForeignKey(ServiceCatalog, on_delete=models.SET_NULL, null=True)
    name_snapshot = models.CharField(max_length=255)
    description_snapshot = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

class WorkOrderItem(BaseModel):
    class ProvidedBy(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        WORKSHOP = "workshop", "Workshop"
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    provided_by = models.CharField(max_length=20, choices=ProvidedBy.choices, default=ProvidedBy.WORKSHOP)
    supplier_name = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

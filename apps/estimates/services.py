from apps.estimates.models import Estimate, EstimateService, EstimateItem
from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from django.db import models
from decimal import Decimal

def calculate_estimate_totals(estimate):
    services_total = estimate.services.aggregate(total=models.Sum('total_price'))['total'] or Decimal('0.00')
    items_total = estimate.items.aggregate(total=models.Sum('total_cost'))['total'] or Decimal('0.00')

    estimate.subtotal = services_total + items_total
    # Simple tax calculation (e.g., 16%)
    estimate.tax_amount = estimate.subtotal * Decimal('0.16')
    estimate.total = estimate.subtotal + estimate.tax_amount - estimate.discount_amount
    estimate.save()

def create_work_order_from_estimate(estimate):
    if estimate.status != Estimate.Status.APPROVED:
        raise ValueError("Only approved estimates can be converted to work orders")

    work_order = WorkOrder.objects.create(
        company=estimate.company,
        customer=estimate.customer,
        vehicle=estimate.vehicle,
        status=WorkOrder.Status.APPROVED
    )

    # Copy services
    for est_service in estimate.services.all():
        WorkOrderService.objects.create(
            work_order=work_order,
            service=est_service.service,
            name_snapshot=est_service.name_snapshot,
            description_snapshot=est_service.description_snapshot,
            quantity=est_service.quantity,
            unit_price=est_service.unit_price,
            total_price=est_service.total_price
        )

    # Copy items
    for est_item in estimate.items.all():
        WorkOrderItem.objects.create(
            work_order=work_order,
            name=est_item.name,
            description=est_item.description,
            quantity=est_item.quantity,
            unit_cost=est_item.unit_cost,
            total_cost=est_item.total_cost,
            provided_by=est_item.provided_by
        )

    estimate.work_order = work_order
    estimate.save()
    return work_order

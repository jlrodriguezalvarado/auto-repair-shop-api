from apps.work_orders.models import WorkOrder, WorkOrderService, WorkOrderItem
from django.db.models import Sum
from decimal import Decimal

def add_service_to_work_order(work_order, service, quantity=1, unit_price=None, notes=None):
    if unit_price is None:
        unit_price = service.base_price
    unit_price = Decimal(str(unit_price))
    return WorkOrderService.objects.create(
        work_order=work_order,
        service=service,
        name_snapshot=service.name,
        description_snapshot=service.description,
        quantity=quantity,
        unit_price=unit_price,
        total_price=unit_price * quantity,
        notes=notes,
    )

def add_item_to_work_order(work_order, name, unit_cost, quantity=1, provided_by="workshop", **kwargs):
    unit_cost = Decimal(str(unit_cost))
    return WorkOrderItem.objects.create(
        work_order=work_order,
        name=name,
        unit_cost=unit_cost,
        quantity=quantity,
        total_cost=unit_cost * quantity,
        provided_by=provided_by,
        **kwargs
    )

def get_work_order_totals(work_order):
    services_total = work_order.services.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
    items_total = work_order.items.aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')
    grand_total = services_total + items_total

    return {
        "services_total": services_total,
        "items_total": items_total,
        "grand_total": grand_total
    }

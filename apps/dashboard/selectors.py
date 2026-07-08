from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.vehicles.models import Vehicle
from apps.receipts.models import Receipt, ReceiptPayment
from apps.work_orders.models import WorkOrder
from apps.catalog.models import ServiceCatalog

class DashboardSelectors:
    @staticmethod
    def get_summary(start_date=None, end_date=None, period=None):
        now = timezone.now()

        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == "current_week":
            start_date = now - timedelta(days=now.weekday())
            end_date = now
        elif period == "current_month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now
        elif not start_date or not end_date:
            # Default to current month
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now

        date_filter = Q(created_at__range=(start_date, end_date))

        vehicles_served_count = WorkOrder.objects.filter(date_filter).values('vehicle').distinct().count()
        pending_receipts = Receipt.objects.filter(status__in=[Receipt.Status.UNPAID, Receipt.Status.PARTIAL])
        pending_receipts_count = pending_receipts.count()
        pending_receipts_total = pending_receipts.aggregate(total=Sum('pending_amount'))['total'] or 0

        received_income_total = ReceiptPayment.objects.filter(payment_date__range=(start_date, end_date)).aggregate(total=Sum('amount'))['total'] or 0

        work_orders_count = WorkOrder.objects.filter(date_filter).count()
        work_orders_by_status = WorkOrder.objects.filter(date_filter).values('status').annotate(count=Count('id'))

        # This is a bit simplified for top services
        from apps.work_orders.models import WorkOrderService
        top_services = WorkOrderService.objects.filter(date_filter).values('name_snapshot').annotate(count=Count('id')).order_by('-count')[:5]

        customers_with_debt = Receipt.objects.filter(pending_amount__gt=0).values('customer__first_name', 'customer__last_name', 'pending_amount').order_by('-pending_amount')[:10]

        recent_payments = ReceiptPayment.objects.order_by('-payment_date')[:10]

        receipts_by_status = Receipt.objects.filter(date_filter).values('status').annotate(count=Count('id'))

        return {
            "vehicles_served_count": vehicles_served_count,
            "pending_receipts_count": pending_receipts_count,
            "pending_receipts_total": pending_receipts_total,
            "received_income_total": received_income_total,
            "work_orders_count": work_orders_count,
            "work_orders_by_status": list(work_orders_by_status),
            "top_services": list(top_services),
            "customers_with_debt": list(customers_with_debt),
            "recent_payments": list(recent_payments.values('id', 'amount', 'payment_date', 'receipt__code')),
            "receipts_by_status": list(receipts_by_status)
        }

from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from apps.receipts.models import Receipt, ReceiptPayment
from apps.work_orders.models import WorkOrder

class DashboardSelectors:
    @staticmethod
    def get_summary(company_id, start_date=None, end_date=None, period=None):
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
            start_date = now.replace(day=1, hour=0, minute=0, second=0)
            end_date = now
        company_filter = Q(company_id=company_id)
        date_filter = Q(created_at__range=(start_date, end_date)) & company_filter
        vehicles_served_count = WorkOrder.objects.filter(date_filter).values("vehicle").distinct().count()
        pending_receipts = Receipt.objects.filter(
            company_id=company_id,
            status__in=[Receipt.Status.UNPAID, Receipt.Status.PARTIAL],
        )
        pending_receipts_count = pending_receipts.count()
        pending_receipts_total = pending_receipts.aggregate(total=Sum("pending_amount"))["total"] or 0
        received_income_total = (
            ReceiptPayment.objects.filter(
                receipt__company_id=company_id,
                payment_date__range=(start_date, end_date),
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        work_orders_count = WorkOrder.objects.filter(date_filter).count()
        work_orders_by_status = WorkOrder.objects.filter(date_filter).values("status").annotate(count=Count("id"))
        from apps.work_orders.models import WorkOrderService
<<<<<<< HEAD
        top_services = (
            WorkOrderService.objects.filter(
                work_order__company_id=company_id,
                created_at__range=(start_date, end_date),
            )
            .values("name_snapshot")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        customers_with_debt = (
            Receipt.objects.filter(company_id=company_id, pending_amount__gt=0)
            .values("customer__first_name", "customer__last_name", "pending_amount")
            .order_by("-pending_amount")[:10]
        )
        recent_payments = ReceiptPayment.objects.filter(receipt__company_id=company_id).order_by("-payment_date")[:10]
        receipts_by_status = Receipt.objects.filter(date_filter).values("status").annotate(count=Count("id"))
=======
        customers_with_debt = [
            {
                "customer_id": row["customer_id"],
                "customer_first_name": row["customer__first_name"],
                "customer_last_name": row["customer__last_name"],
                "pending_amount": row["pending_amount"],
            }
            for row in Receipt.objects.filter(pending_amount__gt=0).values(
                "customer_id", "customer__first_name", "customer__last_name", "pending_amount"
            ).order_by("-pending_amount")[:10]
        ]
        recent_payments = [
            {
                "id": payment.id,
                "amount": payment.amount,
                "payment_date": payment.payment_date,
                "receipt_code": payment.receipt.code if payment.receipt_id else None,
                "customer_first_name": payment.receipt.customer.first_name if payment.receipt_id else "",
                "customer_last_name": payment.receipt.customer.last_name if payment.receipt_id else "",
            }
            for payment in ReceiptPayment.objects.select_related("receipt__customer").order_by("-payment_date")[:10]
        ]
        top_services = [
            {"name": row["name_snapshot"], "count": row["count"]}
            for row in WorkOrderService.objects.filter(date_filter).values("name_snapshot").annotate(count=Count("id")).order_by("-count")[:5]
        ]

        receipts_by_status = Receipt.objects.filter(date_filter).values('status').annotate(count=Count('id'))

>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211
        return {
            "vehicles_served_count": vehicles_served_count,
            "pending_receipts_count": pending_receipts_count,
            "pending_receipts_total": pending_receipts_total,
            "received_income_total": received_income_total,
            "work_orders_count": work_orders_count,
            "work_orders_by_status": list(work_orders_by_status),
<<<<<<< HEAD
            "top_services": list(top_services),
            "customers_with_debt": list(customers_with_debt),
            "recent_payments": list(recent_payments.values("id", "amount", "payment_date", "receipt__code")),
            "receipts_by_status": list(receipts_by_status),
=======
            "top_services": top_services,
            "customers_with_debt": customers_with_debt,
            "recent_payments": recent_payments,
            "receipts_by_status": list(receipts_by_status)
>>>>>>> 57e364fbf09a38203cf48b12a33136d53157d211
        }

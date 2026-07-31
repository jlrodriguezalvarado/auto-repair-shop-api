from apps.notifications.models import Notification
from apps.notifications.services.notification_service import NotificationService

def notify_work_order_status_changed(work_order, *, actor=None):
    recipients = set()
    if work_order.assigned_mechanic_id:
        recipients.add(work_order.assigned_mechanic)
    customer_user = _customer_user(work_order.customer)
    if customer_user:
        recipients.add(customer_user)
    if actor is not None:
        recipients.discard(actor)
    title = f"Orden {work_order.code}"
    body = f"Estado actualizado a {work_order.get_status_display()}"
    data = {
        "url": f"/work-orders/{work_order.id}",
        "workOrderId": work_order.id,
        "status": work_order.status,
    }
    for user in recipients:
        if user is None:
            continue
        NotificationService.create_and_notify(
            user=user,
            notification_type=Notification.TYPE_WORK_ORDER_STATUS,
            title=title,
            body=body,
            data=data,
        )

def notify_work_order_assigned(work_order, *, actor=None):
    mechanic = work_order.assigned_mechanic
    if not mechanic or (actor is not None and mechanic.id == actor.id):
        return
    NotificationService.create_and_notify(
        user=mechanic,
        notification_type=Notification.TYPE_WORK_ORDER_ASSIGNED,
        title=f"Orden asignada {work_order.code}",
        body="Se te asignó una orden de trabajo.",
        data={
            "url": f"/work-orders/{work_order.id}",
            "workOrderId": work_order.id,
        },
    )

def notify_estimate_approved(estimate, *, actor=None):
    recipients = set()
    customer_user = _customer_user(estimate.customer)
    if customer_user:
        recipients.add(customer_user)
    if actor is not None:
        recipients.discard(actor)
    for user in recipients:
        NotificationService.create_and_notify(
            user=user,
            notification_type=Notification.TYPE_ESTIMATE_APPROVED,
            title=f"Presupuesto {estimate.code}",
            body="El presupuesto fue aprobado.",
            data={
                "url": f"/estimates/{estimate.id}",
                "estimateId": estimate.id,
            },
        )

def _customer_user(customer):
    if customer is None:
        return None
    user = getattr(customer, "user", None)
    return user

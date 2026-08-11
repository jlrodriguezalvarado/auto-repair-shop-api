from apps.receipts.models import Receipt, ReceiptPayment
from django.db import models
from decimal import Decimal, InvalidOperation

def calculate_receipt_totals(receipt):
    services_total = receipt.services.aggregate(total=models.Sum('total_price'))['total'] or Decimal('0.00')
    items_total = receipt.items.aggregate(total=models.Sum('total_cost'))['total'] or Decimal('0.00')
    receipt.subtotal = services_total + items_total
    receipt.tax_amount = receipt.subtotal * Decimal('0.16')
    receipt.total = receipt.subtotal + receipt.tax_amount - receipt.discount_amount
    update_receipt_balance(receipt)

def update_receipt_balance(receipt):
    paid_total = receipt.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    receipt.paid_amount = paid_total
    receipt.pending_amount = receipt.total - receipt.paid_amount
    if receipt.paid_amount == 0:
        receipt.status = Receipt.Status.UNPAID
    elif receipt.paid_amount < receipt.total:
        receipt.status = Receipt.Status.PARTIAL
    else:
        receipt.status = Receipt.Status.PAID
    receipt.save()

def _coerce_payment_amount(amount) -> Decimal:
    if amount is None:
        raise ValueError("Amount is required")
    if isinstance(amount, bool):
        raise ValueError("Amount must be a number")
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Amount must be a valid decimal number")
    if not value.is_finite():
        raise ValueError("Amount must be a valid decimal number")
    return value.quantize(Decimal("0.01"))

def add_payment_to_receipt(receipt, amount, payment_method, reference=None, notes=None):
    amount = _coerce_payment_amount(amount)
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > receipt.pending_amount:
        raise ValueError("Payment exceeds pending amount")
    payment = ReceiptPayment.objects.create(
        receipt=receipt,
        amount=amount,
        payment_method=payment_method,
        reference=reference,
        notes=notes
    )
    update_receipt_balance(receipt)
    return payment

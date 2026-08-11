from decimal import Decimal
from django.test import TestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.receipts.models import Receipt, ReceiptService, ReceiptItem
from apps.receipts.services import (
    calculate_receipt_totals,
    add_payment_to_receipt,
)

class ReceiptServicesTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Rec Co",
            tax_id="J-rec",
            address="Addr",
            phone="111",
            email="rec@example.com",
        )
        self.customer = CustomerProfile.objects.create(
            company=self.company,
            first_name="A",
            last_name="B",
            phone="1",
        )
        self.vehicle = Vehicle.objects.create(
            company=self.company,
            customer=self.customer,
            plate="REC-1",
        )
        self.service = ServiceCatalog.objects.create(
            company=self.company,
            name="Brake",
            base_price="100.00",
        )
        self.receipt = Receipt.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
            discount_amount=Decimal("0.00"),
        )

    def test_calculate_receipt_totals_and_unpaid(self):
        ReceiptService.objects.create(
            receipt=self.receipt,
            service=self.service,
            name_snapshot="Brake",
            quantity=1,
            unit_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        ReceiptItem.objects.create(
            receipt=self.receipt,
            name="Pad",
            quantity=1,
            unit_cost=Decimal("50.00"),
            total_cost=Decimal("50.00"),
        )
        calculate_receipt_totals(self.receipt)
        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.subtotal, Decimal("150.00"))
        self.assertEqual(self.receipt.tax_amount, Decimal("24.00"))
        self.assertEqual(self.receipt.total, Decimal("174.00"))
        self.assertEqual(self.receipt.pending_amount, Decimal("174.00"))
        self.assertEqual(self.receipt.status, Receipt.Status.UNPAID)

    def test_partial_then_full_payment(self):
        self.receipt.total = Decimal("100.00")
        self.receipt.pending_amount = Decimal("100.00")
        self.receipt.paid_amount = Decimal("0.00")
        self.receipt.status = Receipt.Status.UNPAID
        self.receipt.save()
        add_payment_to_receipt(self.receipt, Decimal("40.00"), "cash")
        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.paid_amount, Decimal("40.00"))
        self.assertEqual(self.receipt.pending_amount, Decimal("60.00"))
        self.assertEqual(self.receipt.status, Receipt.Status.PARTIAL)
        add_payment_to_receipt(self.receipt, Decimal("60.00"), "card", reference="TX-1")
        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.paid_amount, Decimal("100.00"))
        self.assertEqual(self.receipt.pending_amount, Decimal("0.00"))
        self.assertEqual(self.receipt.status, Receipt.Status.PAID)

    def test_payment_exceeds_pending_rejected(self):
        self.receipt.total = Decimal("50.00")
        self.receipt.pending_amount = Decimal("50.00")
        self.receipt.save()
        with self.assertRaises(ValueError):
            add_payment_to_receipt(self.receipt, Decimal("50.01"), "cash")

    def test_non_positive_payment_rejected(self):
        self.receipt.total = Decimal("50.00")
        self.receipt.pending_amount = Decimal("50.00")
        self.receipt.save()
        with self.assertRaises(ValueError):
            add_payment_to_receipt(self.receipt, Decimal("0.00"), "cash")

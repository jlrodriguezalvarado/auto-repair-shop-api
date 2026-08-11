from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.estimates.models import Estimate, EstimateService, EstimateItem
from apps.estimates.services import calculate_estimate_totals, create_work_order_from_estimate
from apps.work_orders.models import WorkOrder

User = get_user_model()

class EstimateServicesTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Est Co",
            tax_id="J-est",
            address="Addr",
            phone="111",
            email="est@example.com",
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
            plate="EST-1",
        )
        self.service = ServiceCatalog.objects.create(
            company=self.company,
            name="Oil",
            base_price="50.00",
        )
        self.estimate = Estimate.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
            discount_amount=Decimal("0.00"),
        )

    def test_calculate_estimate_totals(self):
        EstimateService.objects.create(
            estimate=self.estimate,
            service=self.service,
            name_snapshot="Oil",
            quantity=2,
            unit_price=Decimal("50.00"),
            total_price=Decimal("100.00"),
        )
        EstimateItem.objects.create(
            estimate=self.estimate,
            name="Filter",
            quantity=1,
            unit_cost=Decimal("25.00"),
            total_cost=Decimal("25.00"),
        )
        calculate_estimate_totals(self.estimate)
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.subtotal, Decimal("125.00"))
        self.assertEqual(self.estimate.tax_amount, Decimal("20.00"))
        self.assertEqual(self.estimate.total, Decimal("145.00"))

    def test_create_work_order_requires_approved(self):
        self.estimate.status = Estimate.Status.DRAFT
        self.estimate.save()
        with self.assertRaises(ValueError):
            create_work_order_from_estimate(self.estimate)

    def test_create_work_order_from_approved_estimate(self):
        EstimateService.objects.create(
            estimate=self.estimate,
            service=self.service,
            name_snapshot="Oil",
            quantity=1,
            unit_price=Decimal("50.00"),
            total_price=Decimal("50.00"),
        )
        self.estimate.status = Estimate.Status.APPROVED
        self.estimate.save()
        work_order = create_work_order_from_estimate(self.estimate)
        self.assertEqual(work_order.status, WorkOrder.Status.APPROVED)
        self.assertEqual(work_order.company_id, self.company.id)
        self.assertEqual(work_order.services.count(), 1)
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.work_order_id, work_order.id)

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.work_orders.models import WorkOrder
from apps.work_orders.services import (
    add_service_to_work_order,
    add_item_to_work_order,
    get_work_order_totals,
)

User = get_user_model()

class WorkOrderServicesTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="WO Co",
            tax_id="J-wo",
            address="Addr",
            phone="111",
            email="wo@example.com",
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
            plate="WO-1",
        )
        self.service = ServiceCatalog.objects.create(
            company=self.company,
            name="Tune",
            base_price="75.00",
        )
        self.work_order = WorkOrder.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
        )

    def test_get_work_order_totals(self):
        add_service_to_work_order(
            self.work_order,
            self.service,
            quantity=2,
            unit_price=Decimal("75.00"),
        )
        add_item_to_work_order(
            self.work_order,
            name="Part",
            unit_cost=Decimal("10.00"),
            quantity=3,
        )
        totals = get_work_order_totals(self.work_order)
        self.assertEqual(totals["services_total"], Decimal("150.00"))
        self.assertEqual(totals["items_total"], Decimal("30.00"))
        self.assertEqual(totals["grand_total"], Decimal("180.00"))

class WorkOrderStatusApiTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="WO Status Co",
            tax_id="J-wos",
            address="Addr",
            phone="111",
            email="wos@example.com",
        )
        self.admin = User.objects.create_user(
            username="wo_admin",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
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
            plate="WOS-1",
        )
        self.work_order = WorkOrder.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
            status=WorkOrder.Status.RECEIVED,
        )

    def test_admin_change_status_transition(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/work-orders/orders/{self.work_order.id}/change_status/",
            {"status": WorkOrder.Status.UNDER_REVIEW},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.work_order.refresh_from_db()
        self.assertEqual(self.work_order.status, WorkOrder.Status.UNDER_REVIEW)

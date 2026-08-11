from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog
from apps.work_orders.models import WorkOrder
from apps.estimates.models import Estimate
from apps.receipts.models import Receipt

User = get_user_model()

class TenantFkAndRbacTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(
            name="Company A",
            tax_id="J-fk-1",
            address="Addr A",
            phone="111",
            email="fk-a@example.com",
        )
        self.company_b = Company.objects.create(
            name="Company B",
            tax_id="J-fk-2",
            address="Addr B",
            phone="222",
            email="fk-b@example.com",
        )
        self.admin_a = User.objects.create_user(
            username="fk_admin_a",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company_a,
        )
        self.mechanic_a = User.objects.create_user(
            username="fk_mech_a",
            password="pass",
            role=User.Role.MECHANIC,
            company=self.company_a,
        )
        self.mechanic_b = User.objects.create_user(
            username="fk_mech_b",
            password="pass",
            role=User.Role.MECHANIC,
            company=self.company_b,
        )
        self.customer_user_a = User.objects.create_user(
            username="fk_cust_a",
            password="pass",
            role=User.Role.CUSTOMER,
            company=self.company_a,
        )
        self.customer_a = CustomerProfile.objects.create(
            company=self.company_a,
            first_name="Alice",
            last_name="A",
            phone="555-1",
            user=self.customer_user_a,
        )
        self.customer_b = CustomerProfile.objects.create(
            company=self.company_b,
            first_name="Bob",
            last_name="B",
            phone="555-2",
        )
        self.vehicle_a = Vehicle.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            plate="FK-AAA",
        )
        self.vehicle_b = Vehicle.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            plate="FK-BBB",
        )
        self.service_a = ServiceCatalog.objects.create(
            company=self.company_a,
            name="Oil A",
            base_price="50.00",
        )
        self.wo_a = WorkOrder.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
            assigned_mechanic=self.mechanic_a,
        )
        self.est_a = Estimate.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
            status=Estimate.Status.SENT,
            subtotal="100.00",
            tax_amount="16.00",
            total="116.00",
        )
        self.rec_a = Receipt.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
            subtotal="100.00",
            tax_amount="16.00",
            total="116.00",
            pending_amount="116.00",
        )

    def test_cross_tenant_work_order_create_rejected(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.post(
            "/api/work-orders/orders/",
            {
                "customer": self.customer_b.id,
                "vehicle": self.vehicle_b.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer", response.data)

    def test_cross_tenant_vehicle_create_rejected(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.post(
            "/api/vehicles/vehicles/",
            {
                "customer": self.customer_b.id,
                "plate": "HACK-1",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer", response.data)

    def test_assign_mechanic_rejects_other_company(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.post(
            f"/api/work-orders/orders/{self.wo_a.id}/assign_mechanic/",
            {"mechanic_id": self.mechanic_b.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.wo_a.refresh_from_db()
        self.assertEqual(self.wo_a.assigned_mechanic_id, self.mechanic_a.id)

    def test_mechanic_cannot_create_work_order(self):
        self.client.force_authenticate(user=self.mechanic_a)
        response = self.client.post(
            "/api/work-orders/orders/",
            {
                "customer": self.customer_a.id,
                "vehicle": self.vehicle_a.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mechanic_can_change_status_on_assigned(self):
        self.client.force_authenticate(user=self.mechanic_a)
        response = self.client.post(
            f"/api/work-orders/orders/{self.wo_a.id}/change_status/",
            {"status": WorkOrder.Status.IN_PROGRESS},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wo_a.refresh_from_db()
        self.assertEqual(self.wo_a.status, WorkOrder.Status.IN_PROGRESS)

    def test_customer_cannot_add_payment(self):
        self.client.force_authenticate(user=self.customer_user_a)
        response = self.client.post(
            f"/api/receipts/receipts/{self.rec_a.id}/add_payment/",
            {
                "amount": "10.00",
                "payment_method": "cash",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_estimate(self):
        self.client.force_authenticate(user=self.customer_user_a)
        response = self.client.post(
            "/api/estimates/estimates/",
            {
                "customer": self.customer_a.id,
                "vehicle": self.vehicle_a.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_approve_estimate(self):
        self.client.force_authenticate(user=self.customer_user_a)
        response = self.client.post(
            f"/api/estimates/estimates/{self.est_a.id}/approve/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.est_a.refresh_from_db()
        self.assertEqual(self.est_a.status, Estimate.Status.APPROVED)

    def test_cross_tenant_order_service_create_rejected(self):
        self.client.force_authenticate(user=self.admin_a)
        service_b = ServiceCatalog.objects.create(
            company=self.company_b,
            name="Oil B",
            base_price="60.00",
        )
        response = self.client.post(
            "/api/work-orders/order-services/",
            {
                "work_order": self.wo_a.id,
                "service": service_b.id,
                "quantity": 1,
                "unit_price": "60.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("service", response.data)

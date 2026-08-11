from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.work_orders.models import WorkOrder
from apps.estimates.models import Estimate
from apps.receipts.models import Receipt

User = get_user_model()

class CrossTenantMutationTests(APITestCase):
    """Tenant A must not retrieve/update/delete tenant B resources."""

    def setUp(self):
        self.company_a = Company.objects.create(
            name="Company A",
            tax_id="J-x-1",
            address="Addr A",
            phone="111",
            email="xa@example.com",
        )
        self.company_b = Company.objects.create(
            name="Company B",
            tax_id="J-x-2",
            address="Addr B",
            phone="222",
            email="xb@example.com",
        )
        self.admin_a = User.objects.create_user(
            username="x_admin_a",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company_a,
        )
        self.customer_b = CustomerProfile.objects.create(
            company=self.company_b,
            first_name="Bob",
            last_name="B",
            phone="555-2",
        )
        self.vehicle_b = Vehicle.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            plate="X-BBB",
        )
        self.wo_b = WorkOrder.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )
        self.est_b = Estimate.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )
        self.rec_b = Receipt.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )

    def test_cannot_retrieve_foreign_customer(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get(f"/api/customers/profiles/{self.customer_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_foreign_customer(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.patch(
            f"/api/customers/profiles/{self.customer_b.id}/",
            {"phone": "hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_foreign_vehicle(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.delete(f"/api/vehicles/vehicles/{self.vehicle_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.vehicle_b.refresh_from_db()
        self.assertIsNone(self.vehicle_b.deleted_at)

    def test_cannot_retrieve_foreign_work_order(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get(f"/api/work-orders/orders/{self.wo_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_foreign_work_order(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.patch(
            f"/api/work-orders/orders/{self.wo_b.id}/",
            {"customer_complaint": "leak"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_foreign_estimate(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.delete(f"/api/estimates/estimates/{self.est_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.est_b.refresh_from_db()
        self.assertIsNone(self.est_b.deleted_at)

    def test_cannot_retrieve_foreign_receipt(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get(f"/api/receipts/receipts/{self.rec_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_add_payment_to_foreign_receipt(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.post(
            f"/api/receipts/receipts/{self.rec_b.id}/add_payment/",
            {"amount": "1.00", "payment_method": "cash"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

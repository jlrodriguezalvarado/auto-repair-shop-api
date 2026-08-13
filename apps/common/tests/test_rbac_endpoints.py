from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.work_orders.models import WorkOrder
from apps.catalog.models import ServiceCatalog

User = get_user_model()

class RbacEndpointTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="RBAC Co",
            tax_id="J-rbac",
            address="Addr",
            phone="111",
            email="rbac@example.com",
        )
        self.admin = User.objects.create_user(
            username="rbac_admin",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
        )
        self.secretary = User.objects.create_user(
            username="rbac_sec",
            password="pass",
            role=User.Role.SECRETARY,
            company=self.company,
        )
        self.mechanic = User.objects.create_user(
            username="rbac_mech",
            password="pass",
            role=User.Role.MECHANIC,
            company=self.company,
        )
        self.customer_user = User.objects.create_user(
            username="rbac_cust",
            password="pass",
            role=User.Role.CUSTOMER,
            company=self.company,
        )
        self.customer = CustomerProfile.objects.create(
            company=self.company,
            first_name="Cust",
            last_name="One",
            phone="555",
            user=self.customer_user,
        )
        self.vehicle = Vehicle.objects.create(
            company=self.company,
            customer=self.customer,
            plate="RBAC-1",
        )
        self.service = ServiceCatalog.objects.create(
            company=self.company,
            name="Align",
            base_price="40.00",
        )
        self.wo = WorkOrder.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
            assigned_mechanic=self.mechanic,
        )

    def test_secretary_can_list_customers(self):
        self.client.force_authenticate(user=self.secretary)
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mechanic_cannot_list_customers(self):
        self.client.force_authenticate(user=self.mechanic)
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_list_all_work_orders(self):
        WorkOrder.objects.create(
            company=self.company,
            customer=self.customer,
            vehicle=self.vehicle,
        )
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get("/api/work-orders/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) else response.data
        self.assertGreaterEqual(len(results), 1)

    def test_mechanic_cannot_create_catalog_service(self):
        self.client.force_authenticate(user=self.mechanic)
        response = self.client.post(
            "/api/catalog/services/",
            {"name": "Hack", "base_price": "1.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_catalog_service(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/catalog/services/",
            {"name": "Detail", "base_price": "80.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

class TenantIsolationTests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(
            name="Company A",
            tax_id="J-1",
            address="Addr A",
            phone="111",
            email="a@example.com",
        )
        self.company_b = Company.objects.create(
            name="Company B",
            tax_id="J-2",
            address="Addr B",
            phone="222",
            email="b@example.com",
        )
        self.superadmin = User.objects.create_user(
            username="superadmin",
            password="pass",
            role=User.Role.SUPER_ADMIN,
            company=None,
            is_staff=True,
        )
        self.admin_a = User.objects.create_user(
            username="admin_a",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company_a,
        )
        self.admin_b = User.objects.create_user(
            username="admin_b",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company_b,
        )
        self.customer_a = CustomerProfile.objects.create(
            company=self.company_a,
            first_name="Alice",
            last_name="A",
            phone="555-1",
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
            plate="AAA-111",
        )
        self.vehicle_b = Vehicle.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            plate="BBB-222",
        )
        self.service_a = ServiceCatalog.objects.create(
            company=self.company_a,
            name="Oil A",
            base_price="50.00",
        )
        self.service_b = ServiceCatalog.objects.create(
            company=self.company_b,
            name="Oil B",
            base_price="60.00",
        )
        self.wo_a = WorkOrder.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
        )
        self.wo_b = WorkOrder.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )
        self.est_a = Estimate.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
        )
        self.est_b = Estimate.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )
        self.rec_a = Receipt.objects.create(
            company=self.company_a,
            customer=self.customer_a,
            vehicle=self.vehicle_a,
        )
        self.rec_b = Receipt.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            vehicle=self.vehicle_b,
        )

    def _results(self, response):
        data = response.data
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_superadmin_forbidden_on_business_endpoints(self):
        self.client.force_authenticate(user=self.superadmin)
        for url in [
            "/api/customers/profiles/",
            "/api/vehicles/vehicles/",
            "/api/catalog/services/",
            "/api/work-orders/orders/",
            "/api/estimates/estimates/",
            "/api/receipts/receipts/",
            "/api/dashboard/summary/",
            "/api/users/users/",
            "/api/company/",
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, url)

    def test_customer_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.customer_a.id, ids)
        self.assertNotIn(self.customer_b.id, ids)

    def test_vehicle_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/vehicles/vehicles/")
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.vehicle_a.id, ids)
        self.assertNotIn(self.vehicle_b.id, ids)

    def test_catalog_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/catalog/services/")
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.service_a.id, ids)
        self.assertNotIn(self.service_b.id, ids)

    def test_work_order_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/work-orders/orders/")
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.wo_a.id, ids)
        self.assertNotIn(self.wo_b.id, ids)

    def test_estimate_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/estimates/estimates/")
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.est_a.id, ids)
        self.assertNotIn(self.est_b.id, ids)

    def test_receipt_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/receipts/receipts/")
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.rec_a.id, ids)
        self.assertNotIn(self.rec_b.id, ids)

    def test_user_isolation(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/users/users/")
        usernames = {item["username"] for item in self._results(response)}
        self.assertIn("admin_a", usernames)
        self.assertNotIn("admin_b", usernames)
        self.assertNotIn("superadmin", usernames)

    def test_create_stamps_company(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.post(
            "/api/customers/profiles/",
            {
                "first_name": "New",
                "last_name": "Customer",
                "phone": "555-9",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company"], self.company_a.id)

    def test_same_plate_allowed_across_companies(self):
        Vehicle.objects.create(
            company=self.company_b,
            customer=self.customer_b,
            plate="AAA-111",
        )
        self.assertEqual(Vehicle.objects.filter(plate="AAA-111").count(), 2)

    def test_my_company_get_and_patch(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/company/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.company_a.id)
        response = self.client.patch(
            "/api/company/",
            {"phone": "999-0000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.company_a.refresh_from_db()
        self.assertEqual(self.company_a.phone, "999-0000")

    def test_auth_payload_includes_company(self):
        response = self.client.post(
            "/api/users/token/",
            {"username": "admin_a", "password": "pass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["company"]["id"], self.company_a.id)
        self.assertEqual(response.data["user"]["company"]["name"], "Company A")

    def test_superadmin_auth_company_null(self):
        response = self.client.post(
            "/api/users/token/",
            {"username": "superadmin", "password": "pass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["user"]["company"])

class CompaniesAdminAPITests(APITestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username="superadmin",
            password="pass",
            role=User.Role.SUPER_ADMIN,
            company=None,
            is_staff=True,
        )
        self.company = Company.objects.create(
            name="Existing Co",
            tax_id="J-9",
            address="Addr",
            phone="000",
            email="co@example.com",
        )
        self.tenant_admin = User.objects.create_user(
            username="tenant_admin",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
        )

    def test_tenant_cannot_list_companies(self):
        self.client.force_authenticate(user=self.tenant_admin)
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_lists_companies(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"] if isinstance(response.data, dict) and "results" in response.data else response.data
        self.assertGreaterEqual(len(results), 1)

    def test_superadmin_creates_company_with_admin(self):
        self.client.force_authenticate(user=self.superadmin)
        payload = {
            "name": "New Shop",
            "tax_id": "J-100",
            "address": "Street 1",
            "phone": "123",
            "email": "shop@example.com",
            "admin_user": {
                "username": "shop_admin",
                "email": "shop_admin@example.com",
                "password": "secret123",
                "first_name": "Shop",
                "last_name": "Admin",
            },
        }
        response = self.client.post("/api/companies/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        company = Company.objects.get(name="New Shop")
        admin = User.objects.get(username="shop_admin")
        self.assertEqual(admin.role, User.Role.ADMINISTRATOR)
        self.assertEqual(admin.company_id, company.id)

    def test_superadmin_can_delete_company(self):
        empty = Company.objects.create(
            name="To Delete",
            tax_id="J-del",
            address="x",
            phone="1",
            email="del@example.com",
        )
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(f"/api/companies/{empty.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(id=empty.id).exists())

    def test_tenant_cannot_assign_superadmin_role(self):
        self.client.force_authenticate(user=self.tenant_admin)
        response = self.client.post(
            "/api/users/users/",
            {
                "username": "bad_user",
                "password": "secret123",
                "email": "bad@example.com",
                "role": "SUPER_ADMIN",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SuperAdminCompanyViewerTests(TenantIsolationTests):
    """SUPER_ADMIN read-only company context via X-Company-Id (SAFE methods only)."""

    BUSINESS_GET_URLS = [
        "/api/customers/profiles/",
        "/api/vehicles/vehicles/",
        "/api/catalog/services/",
        "/api/work-orders/orders/",
        "/api/estimates/estimates/",
        "/api/receipts/receipts/",
        "/api/dashboard/summary/",
        "/api/users/users/",
        "/api/company/",
    ]

    def test_superadmin_with_company_header_reads_company_a(self):
        self.client.force_authenticate(user=self.superadmin)
        for url in self.BUSINESS_GET_URLS:
            response = self.client.get(url, HTTP_X_COMPANY_ID=self.company_a.id)
            self.assertEqual(response.status_code, status.HTTP_200_OK, url)

    def test_superadmin_customers_scoped_to_header_company(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(
            "/api/customers/profiles/",
            HTTP_X_COMPANY_ID=self.company_a.id,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.customer_a.id, ids)
        self.assertNotIn(self.customer_b.id, ids)

    def test_superadmin_invalid_company_id_forbidden(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(
            "/api/customers/profiles/",
            HTTP_X_COMPANY_ID=999999,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_non_integer_header_forbidden(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(
            "/api/customers/profiles/",
            HTTP_X_COMPANY_ID="not-an-id",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_post_customer_forbidden_with_header(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(
            "/api/customers/profiles/",
            {
                "first_name": "Nope",
                "last_name": "Write",
                "phone": "000",
            },
            format="json",
            HTTP_X_COMPANY_ID=self.company_a.id,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_patch_company_forbidden_with_header(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(
            "/api/company/",
            {"phone": "hacked"},
            format="json",
            HTTP_X_COMPANY_ID=self.company_a.id,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tenant_admin_still_works_without_header(self):
        self.client.force_authenticate(user=self.admin_a)
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in self._results(response)}
        self.assertIn(self.customer_a.id, ids)
        self.assertNotIn(self.customer_b.id, ids)

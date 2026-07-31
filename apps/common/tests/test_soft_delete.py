from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile
from apps.vehicles.models import Vehicle
from apps.catalog.models import ServiceCatalog

User = get_user_model()

class SoftDeleteRestoreTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Soft Co",
            tax_id="J-SOFT",
            address="Addr",
            phone="111",
            email="soft@example.com",
        )
        self.admin = User.objects.create_user(
            username="soft_admin",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
        )
        self.superadmin = User.objects.create_user(
            username="soft_super",
            password="pass",
            role=User.Role.SUPER_ADMIN,
            company=None,
            is_staff=True,
        )
        self.customer = CustomerProfile.objects.create(
            company=self.company,
            first_name="Cust",
            last_name="One",
            phone="555",
        )
        self.vehicle = Vehicle.objects.create(
            company=self.company,
            customer=self.customer,
            plate="SOFT-1",
        )
        self.service = ServiceCatalog.objects.create(
            company=self.company,
            name="Brake Job",
            base_price="100.00",
        )

    def _results(self, response):
        data = response.data
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_vehicle_soft_delete_list_filter_and_restore(self):
        self.client.force_authenticate(user=self.admin)
        url = f"/api/vehicles/vehicles/{self.vehicle.id}/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.vehicle.refresh_from_db()
        self.assertIsNotNone(self.vehicle.deleted_at)
        self.assertFalse(Vehicle.objects.filter(pk=self.vehicle.pk).exists())
        self.assertTrue(Vehicle.all_objects.filter(pk=self.vehicle.pk).exists())
        list_default = self.client.get("/api/vehicles/vehicles/")
        self.assertEqual(list_default.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in self._results(list_default)]
        self.assertNotIn(self.vehicle.id, ids)
        list_deleted = self.client.get("/api/vehicles/vehicles/", {"deleted": "true"})
        ids_deleted = [row["id"] for row in self._results(list_deleted)]
        self.assertIn(self.vehicle.id, ids_deleted)
        self.assertIsNotNone(self._results(list_deleted)[0].get("deleted_at"))
        restore = self.client.post(f"/api/vehicles/vehicles/{self.vehicle.id}/restore/")
        self.assertEqual(restore.status_code, status.HTTP_200_OK)
        self.assertIsNone(restore.data.get("deleted_at"))
        self.vehicle.refresh_from_db()
        self.assertIsNone(self.vehicle.deleted_at)
        list_after = self.client.get("/api/vehicles/vehicles/")
        self.assertIn(self.vehicle.id, [row["id"] for row in self._results(list_after)])

    def test_partial_unique_plate_after_soft_delete(self):
        self.client.force_authenticate(user=self.admin)
        self.client.delete(f"/api/vehicles/vehicles/{self.vehicle.id}/")
        create = self.client.post(
            "/api/vehicles/vehicles/",
            {
                "customer": self.customer.id,
                "plate": "SOFT-1",
                "brand": "Toyota",
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data["plate"], "SOFT-1")
        self.assertNotEqual(create.data["id"], self.vehicle.id)

    def test_partial_unique_service_name_after_soft_delete(self):
        self.service.delete()
        ServiceCatalog.objects.create(
            company=self.company,
            name="Brake Job",
            base_price="120.00",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ServiceCatalog.objects.create(
                    company=self.company,
                    name="Brake Job",
                    base_price="130.00",
                )

    def test_partial_unique_username_after_soft_delete(self):
        other = User.objects.create_user(
            username="reuse_me",
            password="pass",
            role=User.Role.SECRETARY,
            company=self.company,
        )
        other.delete()
        recycled = User.objects.create_user(
            username="reuse_me",
            password="newpass",
            role=User.Role.SECRETARY,
            company=self.company,
        )
        self.assertNotEqual(recycled.pk, other.pk)
        self.assertIsNone(recycled.deleted_at)
        login = self.client.post(
            "/api/users/token/",
            {"username": "reuse_me", "password": "newpass"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertEqual(login.data["user"]["id"], recycled.pk)

    def test_soft_deleted_company_blocks_login_and_refresh(self):
        token_resp = self.client.post(
            "/api/users/token/",
            {"username": "soft_admin", "password": "pass"},
            format="json",
        )
        self.assertEqual(token_resp.status_code, status.HTTP_200_OK)
        refresh = token_resp.data["refresh"]
        self.company.delete()
        login_blocked = self.client.post(
            "/api/users/token/",
            {"username": "soft_admin", "password": "pass"},
            format="json",
        )
        self.assertEqual(login_blocked.status_code, status.HTTP_401_UNAUTHORIZED)
        detail = str(login_blocked.data.get("detail", login_blocked.data))
        self.assertIn("company", detail.lower())
        refresh_blocked = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_blocked.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_soft_deleted_user_blocks_login(self):
        self.admin.delete()
        login_blocked = self.client.post(
            "/api/users/token/",
            {"username": "soft_admin", "password": "pass"},
            format="json",
        )
        self.assertEqual(login_blocked.status_code, status.HTTP_401_UNAUTHORIZED)
        detail = str(login_blocked.data.get("detail", login_blocked.data))
        self.assertIn("deleted", detail.lower())

    def test_soft_deleted_company_not_valid_x_company_id(self):
        self.company.delete()
        self.client.force_authenticate(user=self.superadmin)
        resp = self.client.get(
            "/api/company/",
            HTTP_X_COMPANY_ID=str(self.company.id),
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_soft_delete_and_restore_by_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        delete_resp = self.client.delete(f"/api/companies/{self.company.id}/")
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)
        list_default = self.client.get("/api/companies/")
        ids = [row["id"] for row in self._results(list_default)]
        self.assertNotIn(self.company.id, ids)
        restore = self.client.post(f"/api/companies/{self.company.id}/restore/")
        self.assertEqual(restore.status_code, status.HTTP_200_OK)
        self.assertIsNone(restore.data.get("deleted_at"))

    def test_company_hard_delete_by_superadmin(self):
        company_id = self.company.id
        admin_id = self.admin.id
        self.client.force_authenticate(user=self.superadmin)
        soft = self.client.delete(f"/api/companies/{company_id}/")
        self.assertEqual(soft.status_code, status.HTTP_204_NO_CONTENT)
        hard = self.client.post(f"/api/companies/{company_id}/hard-delete/")
        self.assertEqual(hard.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.all_objects.filter(pk=company_id).exists())
        self.assertFalse(User.all_objects.filter(pk=admin_id).exists())

    def test_company_alive_hard_delete_rejected(self):
        self.client.force_authenticate(user=self.superadmin)
        hard = self.client.post(f"/api/companies/{self.company.id}/hard-delete/")
        self.assertEqual(hard.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("soft-deleted", str(hard.data.get("detail", hard.data)).lower())
        self.assertTrue(Company.objects.filter(pk=self.company.id).exists())

    def test_customer_hard_delete_admin_ok_secretary_forbidden(self):
        secretary = User.objects.create_user(
            username="soft_secretary",
            password="pass",
            role=User.Role.SECRETARY,
            company=self.company,
        )
        self.client.force_authenticate(user=self.admin)
        soft = self.client.delete(f"/api/customers/profiles/{self.customer.id}/")
        self.assertEqual(soft.status_code, status.HTTP_204_NO_CONTENT)
        self.client.force_authenticate(user=secretary)
        forbidden = self.client.post(
            f"/api/customers/profiles/{self.customer.id}/hard-delete/"
        )
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomerProfile.all_objects.filter(pk=self.customer.id).exists())
        self.client.force_authenticate(user=self.admin)
        hard = self.client.post(
            f"/api/customers/profiles/{self.customer.id}/hard-delete/"
        )
        self.assertEqual(hard.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomerProfile.all_objects.filter(pk=self.customer.id).exists())

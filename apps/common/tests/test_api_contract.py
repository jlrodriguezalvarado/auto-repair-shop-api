from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company
from apps.customers.models import CustomerProfile

User = get_user_model()

class ApiContractTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Api Co",
            tax_id="J-api",
            address="Addr",
            phone="111",
            email="api@example.com",
        )
        self.admin = User.objects.create_user(
            username="api_admin",
            password="pass",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
        )
        for i in range(12):
            CustomerProfile.objects.create(
                company=self.company,
                first_name=f"C{i}",
                last_name="Test",
                phone=f"555-{i:04d}",
            )

    def test_list_pagination_shape(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["count"], 12)

    def test_validation_error_on_create_customer(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/customers/profiles/",
            {"first_name": "Only"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

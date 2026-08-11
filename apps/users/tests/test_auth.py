from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from apps.company.models import Company

User = get_user_model()

class AuthApiTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Auth Co",
            tax_id="J-auth",
            address="Addr",
            phone="111",
            email="auth@example.com",
        )
        self.user = User.objects.create_user(
            username="auth_user",
            password="secret123",
            role=User.Role.ADMINISTRATOR,
            company=self.company,
        )

    def test_token_obtain_success(self):
        response = self.client.post(
            "/api/users/token/",
            {"username": "auth_user", "password": "secret123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "auth_user")

    def test_token_obtain_invalid_credentials(self):
        response = self.client.post(
            "/api/users/token/",
            {"username": "auth_user", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        obtain = self.client.post(
            "/api/users/token/",
            {"username": "auth_user", "password": "secret123"},
            format="json",
        )
        self.assertEqual(obtain.status_code, status.HTTP_200_OK)
        refresh = self.client.post(
            "/api/users/token/refresh/",
            {"refresh": obtain.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh.data)

    def test_unauthorized_access_returns_401(self):
        response = self.client.get("/api/customers/profiles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bearer_access_token_works(self):
        obtain = self.client.post(
            "/api/users/token/",
            {"username": "auth_user", "password": "secret123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {obtain.data['access']}")
        response = self.client.get("/api/company/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

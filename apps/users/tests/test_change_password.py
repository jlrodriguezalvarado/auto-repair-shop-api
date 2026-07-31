from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class ChangePasswordAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="alice@example.com",
            username="alice",
            password="oldpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("users:change-password")
        self.me_url = reverse("users:user-me")

    def test_change_password_success(self):
        response = self.client.post(
            self.url,
            {
                "current_password": "oldpass123",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Password updated successfully.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass456"))
        self.assertIsNotNone(self.user.tokens_invalid_before)

    def test_change_password_invalid_current_password(self):
        response = self.client.post(
            self.url,
            {
                "current_password": "wrongpass",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("current_password", response.data)

    def test_change_password_mismatch(self):
        response = self.client.post(
            self.url,
            {
                "current_password": "oldpass123",
                "new_password": "newpass456",
                "confirm_password": "differentpass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", response.data)

    def test_change_password_same_as_current(self):
        response = self.client.post(
            self.url,
            {
                "current_password": "oldpass123",
                "new_password": "oldpass123",
                "confirm_password": "oldpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.url,
            {
                "current_password": "oldpass123",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_invalidates_existing_access_token(self):
        self.client.force_authenticate(user=None)
        refresh = RefreshToken.for_user(self.user)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(
            self.url,
            {
                "current_password": "oldpass123",
                "new_password": "newpass456",
                "confirm_password": "newpass456",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        me_response = self.client.get(self.me_url)
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)

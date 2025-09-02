from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:register")
TOKEN_URL = reverse("user:token_obtain_pair")
USER_ME_URL = reverse("user:manage")


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            "email": "public@email.com",
            "password": "password"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_user_already_exist(self):
        payload = {
            "email": "public@email.com",
            "password": "password"
        }
        get_user_model().objects.create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_email_password(self):
        payload = {
            "email": "username",
            "password": "password"
        }
        get_user_model().objects.create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload = {
            "email": "user@email.com",
            "password": "4444"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_user_token(self):
        payload = {
            "email": "public@email.com",
            "password": "password"
        }
        get_user_model().objects.create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_generate_token_user_not_exist(self):
        payload = {
            "email": "public@email.com",
            "password": "password"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_token_credentials_missing(self):
        payload = {
            "email": "public@email.com",
            "password": "password"
        }
        get_user_model().objects.create_user(**payload)

        no_email = {
            "password": "password"
        }
        no_password = {
            "email": "public@email.com",
        }
        res = self.client.post(TOKEN_URL, no_email)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        res = self.client.post(TOKEN_URL, no_password)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(USER_ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="private@email.com",
            password="password"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(USER_ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "id": self.user.id,
                "email": self.user.email,
                "is_staff": self.user.is_staff,
            }
        )

    def test_is_staff_not_changes(self):
        payload = {
            "is_staff": True,
        }
        res = self.client.patch(USER_ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.is_staff, False)

    def test_update_user_information(self):
        payload = {
            "email": "new@email.com",
            "password": "newpassword"
        }
        res = self.client.put(USER_ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import AirplaneType
from airports_management_system.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airports-manager:airplanetype-list")


def sample_type(**params):
    defaults = {
        "name": "Test Type",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_get_list_airplane_types(self):
        sample_type()

        res = self.client.get(AIRPLANE_TYPE_URL)
        types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airplane_type(self):
        payload = {
            "name": "Test Type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "Test Type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        type = AirplaneType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(type.name, payload["name"])

    def test_retrieve_airplane_type(self):
        sample_type()

        res = self.client.get(f"{AIRPLANE_TYPE_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_airplane_type(self):
        sample_type()

        res = self.client.put(
            f"{AIRPLANE_TYPE_URL}1/",
            {"name": "updated type"}
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airplane_type(self):
        sample_type()

        res = self.client.delete(f"{AIRPLANE_TYPE_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import AirplaneType, Airplane
from airports_management_system.serializers import AirplaneListSerializer

AIRPLANE_URL = reverse("airports-manager:airplane-list")


class UnauthenticatedAirplaneApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirplaneApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = AirplaneType.objects.create(name="type 1")

    def test_get_list_airplanes(self):
        Airplane.objects.create(
            name="Airplane",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        airplane = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplane, many=True)

        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

        self.airplane_type = AirplaneType.objects.create(name="type 1")

    def test_create_airplane(self):
        payload = {
            "name": "Airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=res.data["id"])
        airplane_type = payload.pop("airplane_type")
        self.assertEqual(airplane.airplane_type.id, airplane_type)
        for key in payload:
            self.assertEqual(payload[key], getattr(airplane, key))

    def test_retrieve_airplane(self):
        Airplane.objects.create(
            name="Airplane",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        res = self.client.get(f"{AIRPLANE_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_airplane(self):
        Airplane.objects.create(
            name="Airplane",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        res = self.client.put(f"{AIRPLANE_URL}1/", {"name": "Airplane 1"})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airplane(self):
        Airplane.objects.create(
            name="Airplane",
            rows=20,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )

        res = self.client.delete(f"{AIRPLANE_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

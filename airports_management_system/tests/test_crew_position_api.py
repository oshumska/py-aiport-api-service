from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import CrewPosition
from airports_management_system.serializers import CrewPositionSerializer

CREW_POSITION_URL = reverse("airports-manager:crewposition-list")


def sample_position(**params):
    defaults = {
        "name": "Flight attendant"
    }
    defaults.update(params)
    return CrewPosition.objects.create(**defaults)


class UnauthenticatedCrewPositionApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_POSITION_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedCrewPositionApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_crew_positions_list(self):
        """tests that authenticated user have
        access to list crew_positions"""
        sample_position()

        res = self.client.get(CREW_POSITION_URL)

        positions = CrewPosition.objects.all()
        serializer = CrewPositionSerializer(positions, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_crew_position_forbidden(self):
        """tests that not staff can't create crew positions"""
        payload = {
            "name": "Test position"
        }

        res = self.client.post(CREW_POSITION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewPositionApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="<PASSWORD>",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew_position(self):
        payload = {
            "name": "Test position"
        }

        res = self.client.post(CREW_POSITION_URL, payload)

        position = CrewPosition.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(position.name, payload["name"])

    def test_retrieve_crew_position(self):
        sample_position()

        res = self.client.get(f"{CREW_POSITION_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_crew_position(self):
        sample_position()

        res = self.client.put(f"{CREW_POSITION_URL}1/", {"name": "<NAME>"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_crew_position_not_allowed(self):
        sample_position()

        res = self.client.delete(f"{CREW_POSITION_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

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
            username="test",
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

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import Crew, CrewPosition
from airports_management_system.serializers import CrewListSerializer

CREW_URL = reverse("airports-manager:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedCrewApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_get_list_of_crew(self):
        sample_crew()

        crews = Crew.objects.all()
        serializer = CrewListSerializer(crews, many=True)

        res = self.client.get(CREW_URL)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_by_crew_position(self):
        crew = sample_crew()
        position = CrewPosition.objects.create(name="pilot")
        crew_with_position = sample_crew(position=position)
        serializer_1 = CrewListSerializer(crew)
        serializer_2 = CrewListSerializer(crew_with_position)

        res = self.client.get(CREW_URL, {"position": position.id})

        self.assertNotIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

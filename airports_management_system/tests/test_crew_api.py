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


class AdminUserCrewApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }
        res = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_create_crew_with_position(self):
        position = CrewPosition.objects.create(name="pilot")
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "position": position.id
        }
        res = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=res.data["id"])
        position_id = crew.position.id

        self.assertEqual(payload["position"], position_id)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_crew(self):
        sample_crew()

        res = self.client.get(f"{CREW_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_crew(self):
        sample_crew()

        res = self.client.put(f"{CREW_URL}1/", {"first_name": "Jim"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_crew(self):
        sample_crew()

        res = self.client.delete(f"{CREW_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import Country
from airports_management_system.serializers import CountrySerializer

COUNTRY_URL = reverse("airports-manager:country-list")


def sample_country(**params):
    defaults = {
        "name": "Italy",
    }

    defaults.update(params)
    return Country.objects.create(**defaults)


class UnauthenticatedCountryApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COUNTRY_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedCountryApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_get_country_list(self):
        """tests that authenticated user have
               access to list of countries"""
        sample_country()

        res = self.client.get(COUNTRY_URL)

        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_country_forbidden(self):
        """tests that not staff can't create countries"""
        payload = {
            "name": "France",
        }

        res = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserCountryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_country(self):
        """tests that admin can create countries"""
        payload = {
            "name": "France",
        }

        res = self.client.post(COUNTRY_URL, payload)
        country = Country.objects.get(id=res.data["id"])

        self.assertEqual(country.name, payload["name"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_country(self):
        sample_country()

        res = self.client.get(f"{COUNTRY_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_country(self):
        sample_country()

        res = self.client.put(f"{COUNTRY_URL}1/", {"name": "test name"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_country(self):
        sample_country()

        res = self.client.delete(f"{COUNTRY_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

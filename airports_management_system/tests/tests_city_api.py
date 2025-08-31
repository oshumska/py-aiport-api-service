from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import Country, City
from airports_management_system.serializers import CityListSerializer

CITY_URL = reverse("airports-manager:city-list")


class UnauthenticatedCityApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CITY_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedCityApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

        self.country_1 = Country.objects.create(name="test 1")
        self.country_2 = Country.objects.create(name="test 2")
        self.city_1 = City.objects.create(
            country=self.country_1,
            name="test city"
        )
        self.city_2 = City.objects.create(
            country=self.country_2,
            name="test city 2"
        )
        self.city_3 = City.objects.create(
            country=self.country_1,
            name="test city 3"
        )

    def test_get_city_list(self):

        res = self.client.get(CITY_URL)

        city = City.objects.all()
        serializer = CityListSerializer(city, many=True)

        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_city_filter_by_country(self):

        res = self.client.get(CITY_URL, {"country": self.country_1.id})

        serializer_1 = CityListSerializer(self.city_1)
        serializer_2 = CityListSerializer(self.city_2)
        serializer_3 = CityListSerializer(self.city_3)

        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_3.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_city_forbidden(self):
        payload = {
            "country": self.country_1.id,
            "name": "test create"
        }

        res = self.client.post(CITY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

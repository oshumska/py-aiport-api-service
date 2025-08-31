from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import (
    Country,
    City,
    Airport,
)
from airports_management_system.serializers import AirportListSerializer

AIRPORT_URL = reverse("airports-manager:airport-list")


class UnauthenticatedAirportApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirportApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)
        self.country = Country.objects.create(name="Italy")
        self.country_2 = Country.objects.create(name="France")
        self.city = City.objects.create(
            name="Rome",
            country=self.country
        )
        self.city_2 = City.objects.create(
            name="Paris",
            country=self.country_2
        )
        self.airport = Airport.objects.create(
            name="Rome airport",
            closest_big_city=self.city,
        )
        self.airport_2 = Airport.objects.create(
            name="Paris airport",
            closest_big_city=self.city_2,
        )
        self.serializer_1 = AirportListSerializer(self.airport)
        self.serializer_2 = AirportListSerializer(self.airport_2)

    def test_get_list_of_airports(self):
        """tests that authenticated user get list of airports"""
        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_airport_name(self):
        """tests filtering by part of airport name"""
        payload = {
            "name": "Rome"
        }

        res = self.client.get(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, res.data["results"])
        self.assertNotIn(self.serializer_2.data, res.data["results"])

    def test_filter_by_country(self):
        """tests filtering by country id"""
        payload = {
            "country": self.country.id,
        }

        res = self.client.get(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, res.data["results"])
        self.assertNotIn(self.serializer_2.data, res.data["results"])

    def test_filter_by_city(self):
        """tests filtering by city id"""
        payload = {
            "city": self.city.id
        }

        res = self.client.get(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.serializer_1.data, res.data["results"])
        self.assertNotIn(self.serializer_2.data, res.data["results"])

    def test_create_airport_forbidden(self):
        """tests that not staff can't create new airport"""
        payload = {
            "name": "new airport",
            "closest_big_city": self.city.id,
        }

        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirportApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.country = Country.objects.create(name="Italy")
        self.city = City.objects.create(name="Rome", country=self.country)
        self.airport = Airport.objects.create(
            name="test airport",
            closest_big_city=self.city,
        )

    def test_create_airport(self):
        payload = {
            "name": "Rome airport",
            "closest_big_city": self.city.id,
        }

        res = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(airport.name, "Rome airport")
        self.assertEqual(airport.closest_big_city.id, self.city.id)

    def test_retrieve_airport(self):

        res = self.client.get(f"{AIRPORT_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_airport(self):

        res = self.client.put(f"{AIRPORT_URL}1/", {"name": "new name"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airport(self):

        res = self.client.delete(f"{AIRPORT_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

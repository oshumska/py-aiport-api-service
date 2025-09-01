import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import (
    Country,
    City,
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Flight
)
from airports_management_system.serializers import FlightDetailSerializer

FLIGHT_URL = reverse("airports-manager:flight-list")


def sample_airplane(**params):
    type_1 = AirplaneType.objects.create(name="type 1")
    defaults = {
        "name": "Flight attendant",
        "rows": 40,
        "seats_in_row": 5,
        "airplane_type": type_1,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def detail_url(flight_id):
    return reverse("airports-manager:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedFlightApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

        country_1 = Country.objects.create(name="County 1")
        city_1 = City.objects.create(name="City 1", country=country_1)
        airport_1 = Airport.objects.create(
            name="Airport 1",
            closest_big_city=city_1,
        )
        airport_2 = Airport.objects.create(
            name="Airport 2",
            closest_big_city=city_1,
        )
        route_1 = Route.objects.create(
            source=airport_1,
            destination=airport_2,
            distance=100,
        )
        airplane = sample_airplane()
        self.flight_1 = Flight.objects.create(
            route=route_1,
            airplane=airplane,
            departure_time=datetime.datetime(
                2025,
                10,
                10,
                14,
                50,
                tzinfo=datetime.timezone.utc
            ),
            arrival_time=datetime.datetime(
                2025,
                10,
                10,
                16,
                50,
                tzinfo=datetime.timezone.utc
            ),
        )

    def test_get_list_of_flights(self):

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_list_of_flights_filtered_by_date(self):
        payload = {
            "departure_date": "2025-10-10",
            "arrival_date": "2025-10-10",
        }
        for key, value in payload.items():
            res = self.client.get(FLIGHT_URL, {key: value})
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(len(res.data["results"]), 1)

        payload = {
            "departure_date": "2025-10-9",
            "arrival_date": "2025-10-9",
        }
        for key, value in payload.items():
            res = self.client.get(FLIGHT_URL, {key: value})
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(len(res.data["results"]), 0)

    def test_get_list_of_flights_filtered_by_route(self):
        res = self.client.get(FLIGHT_URL, {"route": 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

        res = self.client.get(FLIGHT_URL, {"route": 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 0)

    def test_tickets_available_on_flight_list(self):
        res = self.client.get(FLIGHT_URL)

        self.assertIn("tickets_available", res.data["results"][0].keys())

    def test_retrieve_flight(self):
        url = detail_url(self.flight_1.id)
        res = self.client.get(url)

        serializer = FlightDetailSerializer(self.flight_1, many=False)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tickets_taken_on_flight_detail(self):
        url = detail_url(self.flight_1.id)
        res = self.client.get(url)

        self.assertIn("tickets_taken", res.data.keys())

    def test_update_flight(self):
        url = detail_url(self.flight_1.id)
        res = self.client.put(url, {})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_flight(self):
        res = self.client.post(FLIGHT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight(self):
        url = detail_url(self.flight_1.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

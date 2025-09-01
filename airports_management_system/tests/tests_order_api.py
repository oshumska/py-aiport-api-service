import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import (
    Order,
    Ticket,
    Country,
    City,
    Airport,
    Route,
    Flight,
)
from airports_management_system.tests.tests_flight_api import sample_airplane

ORDER_URL = reverse("airports-manager:order-list")


def sample_order(user):
    return Order.objects.create(user=user)


def sample_ticket(order, flight, row=1, seat=1):
    return Ticket.objects.create(
        order=order,
        flight=flight,
        row=row,
        seat=seat
    )


def sample_flight():
    country = Country.objects.create(name="United Kingdom")
    city = City.objects.create(name="London", country=country)
    airport_1 = Airport.objects.create(name="Airport 1", closest_big_city=city)
    airport_2 = Airport.objects.create(name="Airport 2", closest_big_city=city)
    route = Route.objects.create(
        source=airport_1,
        destination=airport_2,
        distance=100
    )
    airplane = sample_airplane()
    flight = Flight.objects.create(
        route=route,
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
    return flight


class UnauthenticatedOrderApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class UserOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_get_order_list(self):
        order = sample_order(self.user)
        flight = sample_flight()
        sample_ticket(order, flight)

        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        """tests creating an order without tickets,
        and that response not forbidden"""
        res = self.client.post(ORDER_URL, {})

        self.assertNotEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self):
        order = sample_order(self.user)
        flight = sample_flight()
        sample_ticket(order, flight)

        res = self.client.get(f"{ORDER_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order(self):
        order = sample_order(self.user)
        flight = sample_flight()
        sample_ticket(order, flight)

        res = self.client.put(f"{ORDER_URL}1/", data={})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        order = sample_order(self.user)
        flight = sample_flight()
        sample_ticket(order, flight)

        res = self.client.delete(f"{ORDER_URL}1/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_see_only_his_orders(self):
        user_2 = get_user_model().objects.create(
            username="test2",
            email="test2@test.com",
            password="<PASSWORD>"
        )
        order = sample_order(user_2)
        flight = sample_flight()
        sample_ticket(order, flight)

        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 0)

        self.client.force_authenticate(user=user_2)

        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

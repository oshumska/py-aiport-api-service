from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import Country, City, Airport, Route
from airports_management_system.serializers import RouteListSerializer

ROUTE_URL = reverse("airports-manager:route-list")


class UnauthenticatedRouteApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedRouteApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)
        self.country = Country.objects.create(name="source")
        self.country_2 = Country.objects.create(name="destination")
        self.city = City.objects.create(country=self.country, name="source")
        self.city_2 = City.objects.create(
            country=self.country_2,
            name="destination"
        )
        self.airport = Airport.objects.create(
            closest_big_city=self.city,
            name="source"
        )
        self.airport_2 = Airport.objects.create(
            closest_big_city=self.city_2,
            name="destination"
        )
        self.route = Route.objects.create(
            source=self.airport,
            destination=self.airport_2,
            distance=100
        )
        self.route_2 = Route.objects.create(
            source=self.airport_2,
            destination=self.airport, distance=100
        )

    def test_get_list_of_routes(self):
        res = self.client.get(ROUTE_URL)
        route = Route.objects.all()
        serializer = RouteListSerializer(route, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_parameter_id(self):
        """tests filtering for route list for all filtering parameters"""
        payload = {
            "source": self.airport.id,
            "destination": self.airport_2.id,
            "from_country": self.country.id,
            "to_country": self.country_2.id,
        }

        serializer_1 = RouteListSerializer(self.route)
        serializer_2 = RouteListSerializer(self.route_2)

        for key, value in payload.items():
            res = self.client.get(ROUTE_URL, {key: value})

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn(serializer_1.data, res.data["results"])
            self.assertNotIn(serializer_2.data, res.data["results"])

    def test_create_route_forbidden(self):
        payload = {
            "source": self.airport.id,
            "destination": self.airport_2.id,
            "distance": 100,
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

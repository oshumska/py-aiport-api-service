from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


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

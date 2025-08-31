import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airports_management_system.models import AirplaneType, Airplane
from airports_management_system.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airports-manager:airplanetype-list")
AIRPLANE_URL = reverse("airports-manager:airplane-list")


def sample_type(**params):
    defaults = {
        "name": "Test Type",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def image_upload_url(type_id):
    """Return URL to airplane_type image upload"""
    return reverse(
        "airports-manager:airplanetype-upload-image",
        args=[type_id]
    )


class UnauthenticatedAirplaneTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>"
        )
        self.client.force_authenticate(self.user)

    def test_get_list_airplane_types(self):
        sample_type()

        res = self.client.get(AIRPLANE_TYPE_URL)
        types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airplane_type(self):
        payload = {
            "name": "Test Type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserAirplaneTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "Test Type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        type = AirplaneType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(type.name, payload["name"])

    def test_retrieve_airplane_type(self):
        sample_type()

        res = self.client.get(f"{AIRPLANE_TYPE_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_airplane_type(self):
        sample_type()

        res = self.client.put(
            f"{AIRPLANE_TYPE_URL}1/",
            {"name": "updated type"}
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_airplane_type(self):
        sample_type()

        res = self.client.delete(f"{AIRPLANE_TYPE_URL}1/")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ImageFieldAirplaneTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@test.com",
            password="<PASSWORD>",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
        self.type_1 = sample_type()

    def tearDown(self):
        self.type_1.image.delete()

    def test_upload_image_to_airplane_type(self):
        """Tests uploading image to airplane type"""
        url = image_upload_url(self.type_1.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            img = Image.new("RGB", (10, 10))
            img.save(tmp, format="JPEG")
            tmp.seek(0)
            res = self.client.post(url, {"image": tmp}, format="multipart")
        self.type_1.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.type_1.image.path))

    def test_upload_image_bad_request(self):
        """Tests uploading invalid image to airplane type"""
        url = image_upload_url(self.type_1.id)
        res = self.client.post(url, {"image": "image?"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_type(self):
        url = AIRPLANE_TYPE_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            img = Image.new("RGB", (10, 10))
            img.save(tmp, format="JPEG")
            tmp.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "new airplane",
                    "image": tmp
                },
                format="multipart"
            )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane_type = AirplaneType.objects.get(name="new airplane")
        self.assertTrue(airplane_type.image is not None)

    def test_image_url_is_shown_in_airplane_type_list(self):
        url = image_upload_url(self.type_1.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            img = Image.new("RGB", (10, 10))
            img.save(tmp, format="JPEG")
            tmp.seek(0)
            self.client.post(url, {"image": tmp}, format="multipart")
        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertIn("image", res.data["results"][0].keys())

    def test_image_url_is_shown_in_airplane_list(self):
        url = image_upload_url(self.type_1.id)
        Airplane.objects.create(
            airplane_type=self.type_1,
            name="airplane",
            rows=10,
            seats_in_row=5
        )
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            img = Image.new("RGB", (10, 10))
            img.save(tmp, format="JPEG")
            tmp.seek(0)
            self.client.post(url, {"image": tmp}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("airplane_image", res.data["results"][0].keys())

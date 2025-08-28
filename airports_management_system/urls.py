from django.urls import path, include
from rest_framework import routers

from airports_management_system.views import (
    CountryViewSet,
    CityViewSet,
)

app_name = "airports-manager"

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

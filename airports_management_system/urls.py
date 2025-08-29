from django.urls import path, include
from rest_framework import routers

from airports_management_system.views import (
    CountryViewSet,
    CityViewSet,
    CrewPositionViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    RouteViewSet,
    FlightViewSet,
)

app_name = "airports-manager"

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("crew_positions", CrewPositionViewSet)
router.register("crews", CrewViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

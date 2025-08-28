from rest_framework import viewsets, mixins

from airports_management_system.models import (
    Country,
    City,
)
from airports_management_system.serializers import (
    CountrySerializer,
    CitySerializer,
)

class CountryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer

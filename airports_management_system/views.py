from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from django.db.models import F, Count
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from airports_management_system.permissions import (
    IsAdminOrIfAuthenticatedReadOnly
)
from airports_management_system.models import (
    Country,
    City,
    CrewPosition,
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order,
)
from airports_management_system.serializers import (
    CountrySerializer,
    CitySerializer,
    CrewPositionSerializer,
    CrewSerializer,
    CrewListSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    AirportListSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    CityListSerializer,
    AirplaneTypeImageSerializer,
    AirportImageSerializer,
)


class CountryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class CityViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = City.objects.select_related("country")
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        country_str_id = self.request.query_params.get("country")

        queryset = self.queryset

        if country_str_id:
            queryset = queryset.filter(country__id=int(country_str_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer

        return CitySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "country",
                type=OpenApiTypes.INT,
                description="Filter by country id (ex. ?country=1)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of cities"""
        return super().list(request, *args, **kwargs)


class CrewPositionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = CrewPosition.objects.all()
    serializer_class = CrewPositionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.select_related("position")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        return CrewSerializer

    def get_queryset(self):
        position_id_str = self.request.query_params.get("position")

        queryset = self.queryset

        if position_id_str:
            queryset = queryset.filter(position=int(position_id_str))

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "position",
                type=OpenApiTypes.INT,
                description="Filter by CrewPosition id (ex. ?position=1)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of Crews"""
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneTypeImageSerializer

        return AirplaneTypeSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=(IsAdminUser, ),
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane_type = self.get_object()
        serializer = self.get_serializer(airplane_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        return AirplaneSerializer


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Airport.objects.select_related("closest_big_city__country")
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        elif self.action == "upload_image":
            return AirportImageSerializer

        return AirportSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        country_str_id = self.request.query_params.get("country")
        city_str_id = self.request.query_params.get("city")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if country_str_id:
            queryset = queryset.filter(
                closest_big_city__country=int(country_str_id)
            )

        if city_str_id:
            queryset = queryset.filter(closest_big_city=int(city_str_id))

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.select_related(
        "source__closest_big_city__country",
        "destination__closest_big_city__country"
    )
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer

    def get_queryset(self):
        source_str_id = self.request.query_params.get("source")
        destination_str_id = self.request.query_params.get("destination")
        to_country_str_id = self.request.query_params.get("to_country")
        from_country_str_id = self.request.query_params.get("from_country")

        queryset = self.queryset

        if source_str_id:
            queryset = queryset.filter(source=int(source_str_id))

        if destination_str_id:
            queryset = queryset.filter(destination=int(destination_str_id))

        if to_country_str_id:
            to_country = int(to_country_str_id)
            queryset = queryset.filter(
                destination__closest_big_city__country=to_country
            )

        if from_country_str_id:
            from_country = int(from_country_str_id)
            queryset = queryset.filter(
                source__closest_big_city__country=from_country
            )

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .select_related(
            "route__source__closest_big_city__country",
            "airplane__airplane_type",
            "route__destination__closest_big_city__country"
        )
        .prefetch_related("crew_members__position")
        .annotate(
            tickets_available=(
                F("airplane__seats_in_row") * F("airplane__rows")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")
        route_str_id = self.request.query_params.get("route")

        queryset = self.queryset

        if departure_date:
            date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if arrival_date:
            date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=date)

        if route_str_id:
            queryset = queryset.filter(route=int(route_str_id))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route__destination__closest_big_city__country",
        "tickets__flight__route__source__closest_big_city__country",
        "tickets__flight__airplane__airplane_type",
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

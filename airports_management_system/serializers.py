from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airports_management_system.models import (
    Country,
    City,
    CrewPosition,
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight, Ticket, Order,
)


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ("id", "name", "country")


class CrewPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrewPosition
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "position")


class CrewListSerializer(CrewSerializer):
    position = CrewPositionSerializer(many=False, read_only=True)


class CrewDetailSerializer(serializers.ModelSerializer):
    position = serializers.CharField(
        source="position.name",
        read_only=True
    )

    class Meta:
        model = Crew
        fields = ("full_name", "position",)


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=City.objects.select_related("country")
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirportListSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.CharField(
        source="closest_big_city.name"
    )
    country = serializers.CharField(
        source="closest_big_city.country.name"
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city", "country")


class RouteSerializer(serializers.ModelSerializer):
    airport_queryset = Airport.objects.select_related(
        "closest_big_city__country"
    )
    source = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=airport_queryset
    )
    destination = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=airport_queryset
    )

    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs=attrs)
        Route.validate_route(
            attrs["source"],
            attrs["destination"],
            attrs["distance"],
            ValidationError
        )

        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = AirportListSerializer(many=False, read_only=True)
    destination = AirportListSerializer(many=False, read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Route.objects.select_related(
            "destination__closest_big_city__country",
            "source__closest_big_city__country"
        )
    )
    airplane = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Airplane.objects.select_related("airplane_type")
    )
    crew_members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.select_related("position")
    )

    def validate(self, attrs):
        data = super(FlightSerializer, self).validate(attrs=attrs)
        Flight.validate_flight(
            attrs["arrival_time"],
            attrs["departure_time"],
            ValidationError
        )

        return data

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew_members",
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.CharField(source="route.__str__", read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.CharField(
        source="airplane.capacity",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_capacity",
            "departure_time",
            "arrival_time",
            "tickets_available"
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["seat"],
            attrs["row"],
            attrs["flight"].airplane,
            ValidationError
        )

        return data


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatSerializer(TicketSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat",)


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crew_members = CrewDetailSerializer(many=True, read_only=True)
    tickets_taken = TicketSeatSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
            "airplane",
            "tickets_taken",
            "crew_members",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

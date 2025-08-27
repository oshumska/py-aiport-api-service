from rest_framework import serializers

from airports_management_system.models import (
    Country,
    City,
    CrewPosition,
    Crew,
    AirplaneType,
    Airplane,
    Airport,
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

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities",
    )

    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name}({self.country.name})"


class CrewPosition(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.ForeignKey(
        CrewPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crews",
    )

    class Meta:
        verbose_name = "crew member"
        verbose_name_plural = "crew"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}: {self.position.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "airplane type"
        verbose_name_plural = "airplane types"

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departure_routes",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arrival_routes",
    )
    distance = models.IntegerField()

    @property
    def route_name(self):
        source_country = self.source.closest_big_city.country.name
        destination_country = self.destination.closest_big_city.country.name
        return (f"{self.source.name}"
                f"({source_country}) "
                f"-> {self.destination.name}"
                f"({destination_country})")

    @staticmethod
    def validate_route(source, destination, distance, error_to_raise):
        if distance <= 0:
            raise error_to_raise("Distance must be positive")
        if source == destination:
            raise error_to_raise("Source and destination must be different")

    def clean(self):
        Route.validate_route(
            self.source,
            self.destination,
            self.distance,
            ValidationError
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super(Route, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (f"{self.source.closest_big_city.name} "
                f"-> "
                f"{self.destination.closest_big_city.name}")


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew_members = models.ManyToManyField(Crew, blank=True)

    def clean(self):
        if not (self.departure_time
                and self.arrival_time
                and self.departure_time <= self.arrival_time):
            raise ValidationError(
                "Departure time must be earlier than arrival time"
            )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super(Flight, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (f"{self.route.source.closest_big_city.name}"
                f"({self.departure_time}) -> "
                f"{self.route.destination.closest_big_city.name}"
                f"({self.arrival_time})")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    @staticmethod
    def validate_ticket(seat, row, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (seat, "seat", "seats_in_row"),
            (row, "row", "row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {airplane_attr_name}): "
                            f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.row,
            self.flight.airplane,
            ValidationError,
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("row", "seat", "flight")

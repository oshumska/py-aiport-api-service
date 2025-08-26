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
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name} in {self.country.name}"


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
        blank=True
    )

    class Meta:
        verbose_name = "crew member"
        verbose_name_plural = "crew"

    def __str__(self):
        return f"{self.first_name} {self.last_name}: {self.position.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "airplane type"
        verbose_name_plural = "airplane types"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE)
    distance = models.IntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination must be different")
        elif self.distance == 0:
            raise ValidationError("Distance cannot be 0")

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

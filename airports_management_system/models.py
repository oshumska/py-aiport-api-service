from django.db import models

# Create your models here.


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "crew member"
        verbose_name_plural = "crew"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "airplane type"
        verbose_name_plural = "airplane types"

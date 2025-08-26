from django.contrib import admin
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
)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(CrewPosition)
admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Flight)

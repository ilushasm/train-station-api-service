from django.contrib import admin

from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Order,
    Trip,
    Ticket
)

admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Order)
admin.site.register(Trip)
admin.site.register(Ticket)
admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Route)

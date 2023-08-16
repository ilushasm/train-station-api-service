from django.urls import path, include
from rest_framework import routers

from train.views import (
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
    TripViewSet,
    TicketViewSet
)

router = routers.DefaultRouter()
router.register("train-types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("trips", TripViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "train"

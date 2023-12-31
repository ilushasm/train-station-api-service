from rest_framework import routers

from train.views import (
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
    CrewViewSet,
    OrderViewSet,
    TripViewSet,
)

router = routers.DefaultRouter()
router.register("train-types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("trips", TripViewSet)


urlpatterns = router.urls

app_name = "train"

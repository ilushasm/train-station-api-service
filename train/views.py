from typing import Type

from django.db.models import QuerySet, Count, F
from rest_framework import viewsets, mixins
from rest_framework.serializers import Serializer
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
from train.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainRetrieveSerializer,
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    CrewSerializer,
    CrewListSerializer,
    OrderSerializer,
    OrderListSerializer,
    # OrderRetrieveSerializer,
    TripSerializer,
    TripListSerializer,
    TripRetrieveSerializer,
    TicketSerializer
)


class TrainTypeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return TrainRetrieveSerializer
        return TrainSerializer

    def get_queryset(self) -> Type[QuerySet]:
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("trips")
        return queryset


class StationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer

    def get_queryset(self) -> Type[QuerySet]:
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__name__icontains=source)

        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)

        return queryset


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Crew.objects.prefetch_related("assigned_trips")
    serializer_class = CrewSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripRetrieveSerializer
        return TripSerializer

    def get_queryset(self) -> Type[QuerySet]:
        queryset = self.queryset
        departure = self.request.query_params.get("departure")
        arrival = self.request.query_params.get("arrival")
        route = self.request.query_params.get("route")

        if departure:
            queryset = queryset.filter(departure_time__date=departure)

        if arrival:
            queryset = queryset.filter(arrival_time__date=arrival)

        if route:
            queryset = queryset.filter(route__name__icontains=route)

        if self.action in ["list", "retrieve"]:
            queryset = (
                queryset
                .prefetch_related("train")
                .annotate(available_seats=F("train__seats_num") - Count("tickets"))
            )
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self) -> Type[QuerySet]:
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__trip__train")

        return queryset

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)

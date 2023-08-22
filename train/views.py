from typing import Type

from django.db.models import QuerySet, Count, F
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework_simplejwt.authentication import JWTAuthentication

from train.permissions import IsAdminOrReadOnly
from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Order,
    Trip,
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
    TripSerializer,
    TripListSerializer,
    TripRetrieveSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class TrainTypeViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    pagination_class = StandardPagination
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)

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
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (JWTAuthentication,)


class RouteViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = StandardPagination
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = []

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
            queryset = queryset.filter(
                destination__name__icontains=destination
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source station name "
                            "(ex. ?source=lviv)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description=(
                        "Filter by destination station name "
                        "(ex. ?destination=kyiv)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class CrewViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    queryset = Crew.objects.prefetch_related("assigned_trips")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return CrewListSerializer
        return CrewSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.prefetch_related("train__train_type").order_by(
        "departure_time"
    )
    serializer_class = TripSerializer
    pagination_class = StandardPagination
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = []

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
            queryset = queryset.prefetch_related("train").annotate(
                available_seats=F("train__seats_num") - Count("tickets")
            )
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "departure",
                type=OpenApiTypes.DATE,
                description="Filter by departure date "
                            "(ex. ?departure=2023-08-24)"
            ),
            OpenApiParameter(
                "arrival",
                type=OpenApiTypes.DATE,
                description=(
                        "Filter by arrival date "
                        "(ex. ?arrival=2023-08-24)"
                ),
            ),
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by route name "
                    "(ex. ?route=lviv)"
                )
            )
        ]
    )
    def list(self, request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = StandardPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

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

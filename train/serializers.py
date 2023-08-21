from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.db import transaction

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


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    class Meta:
        model = Train
        fields = ("id", "name", "luggage_space", "train_type", "seats_num")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "name", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    class Meta(RouteSerializer.Meta):
        pass


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "departure_time", "arrival_time", "train")


class TripListSerializer(TripSerializer):
    train_type = serializers.CharField(source="train.train_type", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta(TripSerializer.Meta):
        fields = (
            "id",
            "route_name",
            "departure_time",
            "arrival_time",
            "train_type",
            "available_seats"
        )


class TripRetrieveSerializer(TripListSerializer):
    train = TrainSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        source="tickets",
        many=True,
        read_only=True,
        slug_field="seat"
    )

    class Meta(TripListSerializer.Meta):
        fields = (
            "id",
            "route_name",
            "departure_time",
            "arrival_time",
            "train",
            "taken_seats",
            "available_seats"
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "assigned_trips")


class CrewListSerializer(CrewSerializer):
    assigned_trips = TripListSerializer(many=False, read_only=False)

    class Meta(CrewSerializer.Meta):
        pass


class TrainRetrieveSerializer(TrainSerializer):
    trips = serializers.SerializerMethodField()

    class Meta(TrainSerializer.Meta):
        fields = TrainSerializer.Meta.fields + ("trips",)

    @staticmethod
    def get_trips(instance) -> list:
        trips_queryset = instance.trips.all()
        return [trip.route.name for trip in trips_queryset]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs) -> None:
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            seat=attrs["seat"],
            train=attrs["trip"].train,
            luggage_weight=attrs["luggage_weight"],
            error_to_raise=ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("luggage_weight", "seat", "trip")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ("user", "tickets")

    def create(self, validated_data) -> Order:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)

            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)

            return order


class TicketListSerializer(TicketSerializer):
    trip = TripSerializer(many=False, read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

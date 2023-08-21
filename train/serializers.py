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
    train_type = serializers.SlugRelatedField(many=False, read_only=Train, slug_field="name")

    class Meta:
        model = Train
        fields = ("id", "name", "luggage_space", "train_type", "seats_num")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")

    class Meta:
        model = Route
        fields = ("id", "name", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ("id", "route", "departure_time", "arrival_time", "train")


class TripListSerializer(TripSerializer):
    train_info = serializers.CharField(source="train.name", read_only=True)
    train_seats = serializers.IntegerField(source="train.seats_num", read_only=True)
    # available_seats = serializers.IntegerField(read_only=True)

    class Meta(TripSerializer.Meta):
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
            "train_info",
            "train_seats",
            "available_seats"
        )


class TripRetrieveSerializer(TripSerializer):
    bus = TrainSerializer(many=False, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        source="tickets",
        many=True,
        read_only=True,
        slug_field="seat"
    )

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ("taken_seats",)


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

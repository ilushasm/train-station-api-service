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
    route = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    # train = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")
    train = TrainSerializer(many=False, read_only=True)

    class Meta:
        model = Trip
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class TicketSerializer(serializers.ModelSerializer):
    # trip = serializers.SlugRelatedField(many=False, read_only=True, slug_field="route")
    trip = serializers.SlugField(source="trip.route.name")
    departure = serializers.SlugField(source="trip.departure_time")
    arrival = serializers.SlugField(source="trip.arrival_time")

    def validate(self, attrs) -> None:
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            seat=attrs["seat"],
            train=attrs["trip"].train,
            error_to_raise=ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("cargo", "seat", "trip", "departure", "arrival")


class TicketListSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "seat", "cargo")


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    # ticket_list = TicketListSerializer(many=True, read_only=False)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")

    def create(self, validated_data) -> None:
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")

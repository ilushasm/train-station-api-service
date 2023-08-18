from rest_framework.exceptions import ValidationError

from django.db import models
from django.contrib.auth import get_user_model


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=63)
    luggage_space = models.IntegerField()
    seats_num = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")

    def __str__(self) -> str:
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self) -> str:
        return self.name


class Route(models.Model):
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="sources")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="destinations")
    distance = models.IntegerField()

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")

    def __str__(self) -> str:
        return f"{self.user} ({self.created_at})"


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    train_staff = models.ManyToManyField(Crew, related_name="trips")

    def __str__(self) -> str:
        return f"{self.route} [{self.departure_time}]"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("trip", "seat")

    @staticmethod
    def validate_ticket(seat, train, error_to_raise) -> None:
        count_attrs = train.seats_num
        if not (1 <= seat <= count_attrs):
            raise error_to_raise(
                {f"Seat number must be in range [1, {count_attrs}"}
            )

    def __str__(self) -> str:
        return f"Seat: {self.seat}, {self.trip}"

    def clean(self) -> None:
        Ticket.validate_ticket(
            seat=self.seat,
            train=self.trip.train,
            error_to_raise=ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        self.full_clean()
        return super(Ticket, self).save(force_insert, force_update, using, update_fields)

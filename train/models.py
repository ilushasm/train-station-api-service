from django.db import models
from django.contrib.auth import get_user_model


class TrainType(models.Model):
    name = models.CharField(max_length=255)


class Train(models.Model):
    name = models.CharField(max_length=63)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Route(models.Model):
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="sources")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="destinations")
    distance = models.IntegerField()


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="trips")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orders")

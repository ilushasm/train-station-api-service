# Generated by Django 4.2.4 on 2023-08-21 21:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("train", "0007_remove_crew_train_remove_trip_train_staff_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ("created_at",)},
        ),
        migrations.AlterModelOptions(
            name="route",
            options={"ordering": ("name",)},
        ),
        migrations.AlterModelOptions(
            name="train",
            options={"ordering": ("name",)},
        ),
        migrations.AlterModelOptions(
            name="trip",
            options={"ordering": ("departure_time",)},
        ),
    ]

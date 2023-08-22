# Generated by Django 4.2.4 on 2023-08-22 09:55

from django.db import migrations, models
import train.models


class Migration(migrations.Migration):
    dependencies = [
        ("train", "0008_alter_order_options_alter_route_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="station",
            name="image",
            field=models.ImageField(
                null=True, upload_to=train.models.station_image_file_path
            ),
        ),
    ]

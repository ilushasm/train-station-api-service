# Generated by Django 4.2.4 on 2023-08-21 17:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("train", "0004_alter_ticket_order"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ticket",
            old_name="cargo",
            new_name="luggage_weight",
        ),
    ]

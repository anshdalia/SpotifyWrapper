# Generated by Django 5.1.3 on 2024-11-14 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainApp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="wrap",
            name="theme",
            field=models.CharField(
                choices=[
                    ("default", "Default"),
                    ("halloween", "Halloween"),
                    ("christmas", "Christmas"),
                ],
                default="default",
                max_length=10,
            ),
        ),
    ]
# Generated by Django 4.2 on 2023-12-14 16:21

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.CharField(
                        choices=[("H", "Hardcover"), ("S", "Softcover")],
                        default="H",
                        max_length=18,
                    ),
                ),
                ("inventory", models.PositiveIntegerField(default=0)),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=10)),
                ("image", models.CharField(max_length=511)),
            ],
            options={
                "ordering": ["title"],
            },
        ),
    ]

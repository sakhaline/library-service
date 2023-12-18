# Generated by Django 4.2 on 2023-12-18 11:40

import borrowing.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("book", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Borrowing",
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
                ("borrow_date", models.DateTimeField(auto_now_add=True)),
                (
                    "expected_return_date",
                    models.DateTimeField(
                        validators=[borrowing.models.future_date_validator]
                    ),
                ),
                ("actual_return_date", models.DateTimeField(blank=True, null=True)),
                (
                    "books",
                    models.ManyToManyField(related_name="borrowings", to="book.book"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borrowings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

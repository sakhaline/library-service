from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField


class Book(models.Model):
    class CoverChoices(Enum):
        HARD = "H", _("Hardcover")
        SOFT = "S", _("Softcover")

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = EnumField(CoverChoices, default=CoverChoices.HARD, max_length=18)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} by {self.author}"

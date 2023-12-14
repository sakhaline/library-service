import os
import uuid
from enum import Enum

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Book(models.Model):
    class CoverChoices(Enum):
        HARD = "H", _("Hardcover")
        SOFT = "S", _("Softcover")

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = EnumField(CoverChoices, default=CoverChoices.HARD, max_length=18)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(null=True, upload_to=book_image_file_path)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} by {self.author}"

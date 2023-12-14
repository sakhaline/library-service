from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "hard", _("Hard cover")
        SOFT = "soft", _("Soft cover")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=Cover, default=Cover.HARD)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} by {self.author}"

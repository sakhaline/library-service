from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from book.models import Book


def future_date_validator(value):
    if value <= timezone.now():
        raise ValidationError("Expected return date should be in the future.")

    if value <= timezone.now() + timezone.timedelta(days=1):
        raise ValidationError("Minimum borrowing term is one day.")


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField(
        validators=[future_date_validator]
    )
    actual_return_date = models.DateTimeField(blank=True, null=True)
    books = models.ManyToManyField(to=Book, related_name="borrowings")
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        related_name="borrowings"
    )

    @property
    def rent_fee(self):
        total_price = 0
        for book in self.books.all():
            duration = self.expected_return_date - self.borrow_date
            book_price = book.daily_fee * duration.days
            total_price += book_price

        return total_price

    @property
    def over_rent_fee(self):
        total_price = 0
        for book in self.books.all():
            duration = self.actual_return_date - self.expected_return_date
            book_price = book.daily_fee * duration.days
            total_price += book_price

        return total_price

    def __str__(self) -> str:
        return (f"{self.user} on: {self.borrow_date.date()} "
                f"{[book.title for book in self.books.all()]}")

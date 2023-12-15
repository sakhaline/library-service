from django.contrib.auth import get_user_model
from django.db import models

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(blank=True, null=True)
    books = models.ManyToManyField(Book, related_name="borrowings")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self) -> str:
        return f"{self.user} on: {self.borrow_date.date()} {[book.title for book in self.books.all()]}"

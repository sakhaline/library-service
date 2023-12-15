from rest_framework import serializers

from borrowing.models import Borrowing
from book.serializer import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "actual_return_date", "book", )

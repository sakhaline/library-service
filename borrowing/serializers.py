from rest_framework import serializers

from borrowing.models import Borrowing
from book.serializers import BookListSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    # book = BookListSerializer(many=True, read_only=True)
    book = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

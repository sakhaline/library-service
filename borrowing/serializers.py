from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.models import Book
from book.serializers import BookListSerializer
from borrowing.models import Borrowing
from payment.sessions import create_payment_session
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    books = serializers.SlugRelatedField(many=True, read_only=True, slug_field="title")
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "user", "borrow_date", "expected_return_date", "books", "rent_fee", )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    books = serializers.PrimaryKeyRelatedField(many=True, queryset=Book.objects.all())

    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "books", )

    @transaction.atomic()
    def create(self, validated_data):
        books = validated_data.pop("books")
        borrowing = Borrowing.objects.create(**validated_data)
        for book in books:
            if book.inventory:
                book.inventory -= 1
                borrowing.books.add(book)
                book.save()
            else:
                raise ValidationError({"books": "Some of books are out of inventory."})
        return borrowing


class BorrowingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "books", "actual_return_date", )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    books = BookListSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = ("borrow_date", "expected_return_date", "actual_return_date", "books", "user", )


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "books",
        )

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("This book has already been "
                                              "returned.")
        return attrs

from rest_framework import serializers

from book.models import Book


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        ]


class BookDetailSerializer(BookListSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "image",
        ]


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "image",
        )

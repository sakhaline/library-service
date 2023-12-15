from rest_framework import serializers

from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    books = serializers.SlugRelatedField(many=True, read_only=True, slug_field="title")
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "user", "borrow_date", "expected_return_date", "books", )

    def create(self, validated_data):
        return Borrowing.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.expected_return_date = validated_data.get("expected_return_date", instance.expected_return_date)
        instance.actual_return_date = validated_data.get("actual_return_date", instance.actual_return_date)
        instance.books = validated_data.get("books", instance.book)
        instance.save()

        return instance


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

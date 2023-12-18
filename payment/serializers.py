from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "borrowing_id",
            "money_to_pay",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(
        source="borrowing_id.user.id", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "user_id",
            "money_to_pay",
            "session_url",
            "session_id",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(
        source="borrowing_id.user.email", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "user_email",
            "session_url",
            "session_id",
            "money_to_pay",
        )

import stripe
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from service_config import settings
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer
)


stripe.api_key = settings.STRIPE_API_KEY


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        borrowing_id = self.request.query_params.get("borrowing_id")

        queryset = self.queryset

        if borrowing_id:
            queryset = queryset.filter(borrowing__id=borrowing_id)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer

        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="success",
    )
    def success(self, request, pk=None):
        payment = self.get_object()
        serializer = self.get_serializer(payment)

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment.session_id)
            if payment_intent.status == 'succeeded':
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Payment not succeeded"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        payment = self.get_object()
        serializer = self.get_serializer(payment)

        try:
            refund = stripe.Refund.create(
                payment_intent=payment.session_id
            )

            if refund.status == 'succeeded':
                payment.status = Payment.StatusChoices.PENDING
                payment.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

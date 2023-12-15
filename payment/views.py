import stripe
from django.shortcuts import get_object_or_404
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

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                borrowing_id__user_id=self.request.user.id
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        elif self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    @action(
        methods=["GET"],
        detail=True,
        url_path="success",
    )
    def success(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)

        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment.session_id)

            if payment_intent.status == 'succeeded':
                payment.status = Payment.StatusChoices.PAID
                payment.save()

                serializer = self.get_serializer(payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Payment not succeeded"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except stripe.error.StripeError as e:
            return Response(
                {"detail": f"Stripe error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)

        try:
            refund = stripe.Refund.create(payment_intent=payment.session_id)

            if refund.status == 'succeeded':
                payment.status = Payment.StatusChoices.PENDING
                payment.save()

                serializer = self.get_serializer(payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Refund not succeeded"},
                                status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            return Response(
                {"detail": f"Stripe error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

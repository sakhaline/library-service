import stripe
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from notifications.telegram_notifications import payment_notification
from service_config import settings
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

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
            if not payment.session_url:
                return Response(
                    {"detail": "Payment does not have a valid session_url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            session = stripe.checkout.Session.retrieve(payment.session_id)
            if (session.payment_status == "paid" and payment.status !=
                    Payment.StatusChoices.PAID):
                payment_notification(
                    user=payment.borrowing_id.user,
                    borrow=payment.borrowing_id,
                )
                payment.status = Payment.StatusChoices.PAID
                payment.save()

                serializer = self.get_serializer(payment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif (session.payment_status == "paid" and payment.status ==
                    Payment.StatusChoices.PAID):
                return Response({"detail": "Payment already successful!"},
                                status=status.HTTP_400_BAD_REQUEST,)
            else:
                return Response(
                    {"detail": "Payment not succeeded!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except stripe.error.StripeError as e:
            return Response(
                {"detail": f"Stripe error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        methods=["GET"],
        detail=True,
        url_path="cancel",
    )
    def cancel(self, request, pk=None):
        payment = get_object_or_404(Payment, pk=pk)
        session = stripe.checkout.Session.retrieve(payment.session_id)

        if (session.payment_status == "unpaid" and payment.status ==
                Payment.StatusChoices.PENDING):
            return Response(
                {
                    "detail": "Payment can be paid a bit later (but the "
                              "session is available for only 24h)",
                    "payment_link": f"{payment.session_url}"
                 },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Payment was succeed",
                },
                status=status.HTTP_200_OK,
            )

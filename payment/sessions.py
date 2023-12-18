from decimal import Decimal

import stripe
from django.urls import reverse

from payment.models import Payment
from service_config import settings
from service_config.settings import BASE_URL

stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2


def initialize_payment(borrowing, payment_type):
    return Payment.objects.create(
        borrowing_id=borrowing, payment_type=payment_type, money_to_pay=0
    )


def update_payment(payment_instance, session):
    payment_instance.status = Payment.StatusChoices.PENDING
    payment_instance.session_url = session.url
    payment_instance.session_id = session.id
    payment_instance.money_to_pay = session.amount_total / 100
    payment_instance.save()


def create_payment_session(borrowing, days: int = None):
    books = [book.title for book in borrowing.books.all()]

    if days:
        amount = (
            int(Decimal(borrowing.over_rent_fee) * Decimal(100))
            * FINE_MULTIPLIER
        )

        payment_type = Payment.TypeChoices.FINE
    else:
        amount = int(Decimal(borrowing.rent_fee) * Decimal(100))
        payment_type = Payment.TypeChoices.PAYMENT

    try:
        payment_instance = initialize_payment(
            borrowing=borrowing, payment_type=payment_type
        )
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": ", ".join(books),
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{BASE_URL}"
            f"{reverse('payment:success', args=[payment_instance.pk])}",
            cancel_url=f"{BASE_URL}"
            f"{reverse('payment:cancel', args=[payment_instance.pk])}",
        )
        update_payment(payment_instance=payment_instance, session=session)
        return session

    except Exception as e:
        return {"error": str(e)}

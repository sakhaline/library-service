import stripe

from django.urls import reverse
from decimal import Decimal
from service_config import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
API_URL = "http://127.0.0.1:8000"
FINE_MULTIPLIER = 2


def create_payment(borrowing, session, payment_type):
    Payment.objects.create(
        status="Pending",
        payment_type=payment_type,
        borrowing_id=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=session.amount_total,
    )
    print("CREATED PAYMENT")


def create_payment_session(borrowing, days: int = None):
    if days:
        amount = (int(Decimal(borrowing.over_rent_fee) * Decimal(100)) *
                  FINE_MULTIPLIER)
        payment_type = "Fine"
    else:
        amount = int(Decimal(borrowing.rent_fee) * Decimal(100))
        payment_type = "Payment"

    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Borrowed books",
                        },
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{API_URL}{reverse('payment:success')}"
                        + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=f"{API_URL}{reverse('payment:cancel')}"
                       + "?session_id={CHECKOUT_SESSION_ID}",
        )
        create_payment(borrowing, session, payment_type)
        return session
    except Exception as e:
        return {"error": str(e)}

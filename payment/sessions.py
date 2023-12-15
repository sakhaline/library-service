import stripe

from django.urls import reverse

from service_config import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
API_URL = "http/locahost:8000"
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


def create_payment_session(borrowing, days: int = None):
    if days:
        amount = int(borrowing.book.daily_fee) * days * 100 * FINE_MULTIPLIER
        payment_type = "FINE"
    else:
        days = (borrowing.expected_return_date - borrowing.borrow_date).days
        amount = int(borrowing.book.daily_fee) * days * 100
        payment_type = "PAYMENT"

    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"{borrowing.book.title} borrowing for {days} days",
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

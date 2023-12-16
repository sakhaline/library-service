import stripe

from django.urls import reverse
from decimal import Decimal
from service_config import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY
API_URL = "http/127.0.0.1:8000"
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


def create_payment_session(borrowing, book_titles_list, days: int = None):
    print("START")
    # if days:
    #     amount = int(borrowing.rent_fee) * days * 100 * FINE_MULTIPLIER
    #     payment_type = "Fine"
    # else:
    #     days = (borrowing.expected_return_date - borrowing.borrow_date).days
    #     amount = int(borrowing.books.daily_fee) * days * 100
    #     borrowing.rent_fee borrowing.rent_fee * Decimal(100)
    payment_type = "Payment"
    print(borrowing.rent_fee * Decimal(100))

    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Borrowed books",
                        },
                        "unit_amount": 10.00,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel?session_id={CHECKOUT_SESSION_ID}",
        )
        print(session)
        create_payment(borrowing, session, payment_type)
        return session
    except Exception as e:
        return {"error": str(e)}

    # try:
    #     print("START SESSION")
    #     session = stripe.checkout.Session.create(
    #         line_items=[
    #             {
    #                 "price_data": {
    #                     "currency": "usd",
    #                     "product_data": {
    #                         "name": f" borrowing",
    #                     },
    #                     "unit_amount": 1, 2,
    #                 },
    #                 "quantity": 1,
    #             }
    #         ],
    #         mode="payment",
    #         success_url=f"{API_URL}{reverse('payment:success')}"
    #         + "?session_id={CHECKOUT_SESSION_ID}",
    #         cancel_url=f"{API_URL}{reverse('payment:cancel')}"
    #         + "?session_id={CHECKOUT_SESSION_ID}",
    #     )
    #     print(session)
    #     print("SESSION")
    #     create_payment(borrowing, session, payment_type)
    #     print(session)
    #     return session
    # except Exception as e:
    #     print("EXEPTION")
    #     return {"error": str(e)}

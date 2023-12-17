from datetime import timedelta

import stripe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentDetailSerializer, PaymentListSerializer
from service_config.settings import BASE_URL

PAYMENT_URL = reverse("payment:payment-list")


def sample_user(**params):
    defaults = {
        "email": "test@gmail.com",
        "first_name": "name",
        "last_name": "last name",
        "password": "testpass",
    }
    defaults.update(params)

    return get_user_model().objects.create(**defaults)


def sample_book(**params):
    defaults = {
        "title": "book",
        "author": "author",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 2.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    defaults = {
        "expected_return_date": timezone.now() + timedelta(days=10),
        "user": sample_user(),
    }
    defaults.update(params)
    borrowing = Borrowing.objects.create(**defaults)
    books = sample_book()
    borrowing.books.set([books])
    return borrowing


def detail_url(payment_id):
    return reverse("payment:payment-detail", args=[payment_id])


class UnauthenticatedPaymentApiTests(TestCase):
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PAYMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpass", is_staff=False
        )
        borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            user=self.user,
        )
        defaults = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing_id": borrowing,
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }

        self.payment = Payment.objects.create(**defaults)

        self.test_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Bookname",
                        },
                        "unit_amount": 5000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{BASE_URL}{reverse('payment:success', args=[self.payment.id])}",
            cancel_url=f"{BASE_URL}{reverse('payment:cancel', args=[self.payment.id])}",
        )

        self.valid_session_id = self.test_session.id

        self.payment.session_id = self.valid_session_id
        self.payment.save()

        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        payment1 = self.payment
        payload = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing_id": sample_borrowing(),
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        payment2 = Payment.objects.create(**payload)
        res = self.client.get(PAYMENT_URL)

        serializer1 = PaymentListSerializer(payment1)
        serializer2 = PaymentListSerializer(payment2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_payment_detail(self):
        payment1 = self.payment

        url = detail_url(payment1.id)
        res = self.client.get(url)

        serializer = PaymentDetailSerializer(self.payment)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_success_cancel_for_unpaid_session(self):
        payment1 = self.payment

        url1 = reverse("payment:success", args=[payment1.id])
        url2 = reverse("payment:cancel", args=[payment1.id])

        res1 = self.client.get(url1)
        res2 = self.client.get(url2)

        bad_response = Response(
            {"detail": "Payment not succeeded!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.data, bad_response.data)

    def test_refund_is_not_allowed_for_user(self):
        payment1 = self.payment

        url = reverse("payment:refund", args=[payment1.id])

        res = self.client.get(url)

        expected_response = Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.data, expected_response.data)


class AdminPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpass", is_staff=True
        )
        borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timedelta(days=10),
            user=self.user,
        )
        defaults = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing_id": borrowing,
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }

        self.payment = Payment.objects.create(**defaults)

        self.test_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Bookname",
                        },
                        "unit_amount": 5000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{BASE_URL}{reverse('payment:success', args=[self.payment.id])}",
            cancel_url=f"{BASE_URL}{reverse('payment:cancel',args=[self.payment.id])}",
        )

        self.valid_session_id = self.test_session.id

        self.payment.session_id = self.valid_session_id
        self.payment.save()

        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        payment1 = self.payment
        payload = {
            "status": "PENDING",
            "payment_type": "PAYMENT",
            "borrowing_id": sample_borrowing(),
            "session_url": "http://127.0.0.1:8000/api/payments/",
            "session_id": "some id",
            "money_to_pay": 2.00,
        }
        payment2 = Payment.objects.create(**payload)
        res = self.client.get(PAYMENT_URL)

        serializer1 = PaymentListSerializer(payment1)
        serializer2 = PaymentListSerializer(payment2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_refund_payment_not_succeed_but_allowed_for_admin(self):
        payment1 = self.payment

        url = reverse("payment:refund", args=[payment1.id])

        res = self.client.get(url)

        bad_response = Response(
            {
                "detail": "Your payment intent is not defined "
                "(You don't make any payments)",
                "payment": payment1.session_id,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, bad_response.data)
        self.assertNotEquals(res.status_code, status.HTTP_403_FORBIDDEN)

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentDetailSerializer, PaymentListSerializer


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
            "test@test.com",
            "testpass",
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

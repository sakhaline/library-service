import os
import tempfile
from unittest import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from book.models import Book
from book.serializers import BookDetailSerializer, BookListSerializer

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "H",
        "inventory": "5",
        "daily_fee": "3",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_book_detailed(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Sample Author",
        "cover": "H",
        "inventory": 5,
        "daily_fee": 3,
        "image": "someurl.com",
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def image_upload_url(book_id):
    """Return URL for book image upload"""
    return reverse("book:book-upload-image", args=[book_id])


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books_unauthenticated(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        email = "test@test.com"
        if not get_user_model().objects.filter(email=email).exists():
            self.user = get_user_model().objects.create_user(email, "testpass")
        else:
            self.user = get_user_model().objects.get(email=email)

        self.client.force_authenticate(self.user)

    def test_list_books_authenticated(self):
        sample_book()
        sample_book()

        response = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book_detailed()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Sample Book",
            "author": "Sample Author",
            "cover": "H",
            "inventory": 5,
            "daily_fee": 3,
            "image": "someurl.com",
        }
        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Sample Book",
            "author": "Sample Author",
            "cover": "H",
            "inventory": 5,
            "daily_fee": 3,
        }
        response = self.client.post(BOOK_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=response.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_update_book(self):
        book = sample_book()

        updated_payload = {
            "title": "Updated Title",
            "author": "Updated Author",
            "cover": "S",
            "inventory": 10,
            "daily_fee": 5,
        }

        url = detail_url(book.id)
        response = self.client.put(url, updated_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        for key in updated_payload.keys():
            self.assertEqual(updated_payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()

        url = detail_url(book.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=book.id)


class BookImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        existing_user = (
            get_user_model()
            .objects.filter(email="admin@myproject.com")
            .first()
        )

        if not existing_user:
            self.user = get_user_model().objects.create_superuser(
                "admin@myproject.com", "password"
            )
        else:
            self.user = existing_user

        self.client.force_authenticate(self.user)
        self.book = sample_book_detailed()

    def tearDown(self):
        self.book.image.replace(self.book.image, "")

    def test_upload_image_to_book(self):
        """Test uploading an image to book"""
        url = image_upload_url(self.book.id)
        response = self.client.post(url, {"image": "some-url.com"})
        self.book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertEqual(self.book.image, "some-url.com")

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.book.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = self.client.post(
                url, {"image": ntf}, format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_book_list_should_not_work(self):
        url = BOOK_URL
        response = self.client.post(url, {"image": "some-url.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        book = Book.objects.filter(title="Title").first()
        self.assertFalse(book)

    def test_image_is_shown_on_book_detail(self):
        url = image_upload_url(self.book.id)
        self.client.post(url, {"image": "some_url.com"})
        res = self.client.get(detail_url(self.book.id))

        self.assertIn("image", res.data)

    def test_image_url_is_not_shown_on_movie_list(self):
        url = image_upload_url(self.book.id)
        self.client.post(url, {"image": "some_url.com"})
        res = self.client.get(BOOK_URL)

        self.assertNotIn("image", res.data[0].keys())

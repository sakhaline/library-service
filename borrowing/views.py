from django.utils import timezone

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book.models import Book
from borrowing.models import Borrowing

from payment.sessions import create_payment_session
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
)
from notifications.telegram_notifications import borrowing_notification


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.prefetch_related("books")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        book_titles_list = list(
            Book.objects.filter(id__in={**self.request.data}.get("books")).values_list(
                "title", flat=True
            )
        )
        create_payment_session(
            borrowing=serializer.instance,
        )
        borrowing_notification(
            user=self.request.user,
            borrow=serializer.instance,
            books_names=book_titles_list,
        )

    def list(self, request, *args, **kwargs):
        is_active = self.request.query_params.get("is_active", None)
        user_id = self.request.query_params.get("user_id", None)

        if is_active is not None and is_active.lower() == "true":
            queryset = self.queryset.filter(actual_return_date__isnull=True)
        else:
            queryset = self.queryset.all()

        if not self.request.user.is_staff and user_id is None:
            queryset = queryset.filter(user=self.request.user)
        elif user_id is not None:
            queryset = queryset.filter(user__id=user_id)

        serializer = BorrowingSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset.all()
        else:
            queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "update":
            return BorrowingUpdateSerializer

        return BorrowingSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
    )
    def return_book(self, request, pk):
        with transaction.atomic():
            borrowing = get_object_or_404(Borrowing, id=pk)
            serializer = BorrowingReturnSerializer(
                borrowing, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)

            if borrowing.actual_return_date:
                return Response(
                    {"error": "These books has already been returned."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            borrowing.actual_return_date = timezone.now()
            borrowing.save()

            if borrowing.actual_return_date > borrowing.expected_return_date:
                days = (
                    borrowing.actual_return_date.date()
                    - borrowing.expected_return_date.date()
                ).days
                create_payment_session(borrowing, days)

            books = borrowing.books.all()
            for book in books:
                book.inventory += 1
                book.save()

            serializer.save()
            response_serializer = BorrowingDetailSerializer(borrowing)
            data = {
                "message": "Books returned successfully.",
                "borrowing_details": response_serializer.data,
            }
            return Response(data, status=status.HTTP_200_OK)

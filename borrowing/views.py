import datetime

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)
from notifications.telegram_notifications import borrowing_notification


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.prefetch_related("books")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        print(serializer.instance.rent_fee)
        book_titles_list = list(
            Book.objects.filter(
                id__in={**self.request.data}.get("books")
            ).values_list("title", flat=True)
        )
        borrowing_notification(
            user=self.request.user,
            borrow=serializer.instance,
            books_names=book_titles_list,
            all_tickets_url="http://127.0.0.1:8000/api/borrowings/borrowings/",
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
        # print(self.action)
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "create":
            return BorrowingDetailSerializer

        return BorrowingSerializer

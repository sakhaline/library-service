from django.utils import timezone

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (BorrowingSerializer,
                                   BorrowingReturnSerializer)
from payment.sessions import create_payment_session


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.prefetch_related("books")
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.id)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user.id)
        return queryset

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
            borrowing.actual_return_date = timezone.now()
            borrowing.save()
            if borrowing.actual_return_date > borrowing.expected_return_date:
                days = (
                        borrowing.actual_return_date.date()
                        - borrowing.expected_return_date.date()
                ).days
                create_payment_session(borrowing, days)
            books = borrowing.books
            books.inventory += 1
            books.save()
            serializer.save()
            response_serializer = BorrowingSerializer(borrowing)
            # change  BorrowingSerializer -> BorrowingDetailSerializer
            return Response(response_serializer.data,
                            status=status.HTTP_200_OK)


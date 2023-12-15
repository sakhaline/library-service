from django.urls import path, include
from rest_framework import routers

from borrowing.views import (
    BorrowingViewSet
)

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/return",
        BorrowingViewSet.as_view({"post": "return_book"}),
        name="return",
    ),
]

app_name = "borrowing"

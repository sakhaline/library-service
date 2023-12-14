from django.urls import path, include
from rest_framework import routers

from book.views import BookListViewSet

router = routers.DefaultRouter()
router.register("books", BookListViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "book"

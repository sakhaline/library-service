from django.urls import include, path
from rest_framework import routers

from payment.views import PaymentViewSet

router = routers.DefaultRouter()

router.register("", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/success/",
        PaymentViewSet.as_view({"get": "success"}),
        name="success",
    ),
    path(
        "<int:pk>/cancel/",
        PaymentViewSet.as_view({"get": "cancel"}),
        name="cancel",
    ),
    path(
        "<int:pk>/refund/",
        PaymentViewSet.as_view({"get": "refund"}),
        name="refund",
    ),
]

app_name = "payment"

from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField
from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusChoices(Enum):
        PENDING = "P", _("Pending")
        PAID = "P", _("Paid")

    class TypeChoices(Enum):
        PAYMENT = "P", _("Payment")
        FINE = "F", _("Fine")

    status = EnumField(
        StatusChoices, max_length=16, default=StatusChoices.PENDING
    )
    payment_type = EnumField(
        TypeChoices, max_length=16, default=TypeChoices.PAYMENT
    )
    borrowing_id = models.ForeignKey(
        Borrowing, models.CASCADE, related_name="payments"
    )
    session_url = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=3, decimal_places=2)

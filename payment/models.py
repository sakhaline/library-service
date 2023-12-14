from django.db import models
from enum import Enum
from django.utils.translation import gettext_lazy as _
from enumfields import EnumField


class Payment(models.Model):
    class StatusChoices(Enum):
        PENDING = "P", _("Pending")
        Paid = "P", _("Paid")

    class TypeChoices(Enum):
        PAYMENT = "P", _("Payment")
        FINE = "F", _("Fine")

    status = EnumField(StatusChoices, default=StatusChoices.PENDING)
    type = EnumField(TypeChoices, default=TypeChoices.PAYMENT)
    borrowing_id = models.IntegerField()
    session_url = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField()

from django.db import models
from django.utils.translation import gettext_lazy as _
from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'P', _('Pending')
        PAID = 'I', _('Paid')

    class TypeChoices(models.TextChoices):
        PAYMENT = 'P', _('Payment')
        FINE = 'F', _('Fine')

    status = models.CharField(
        max_length=16,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    payment_type = models.CharField(
        max_length=16,
        choices=TypeChoices.choices,
        default=TypeChoices.PAYMENT
    )
    borrowing_id = models.ForeignKey(
        Borrowing, models.CASCADE, related_name="payments"
    )
    session_url = models.CharField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

from django.utils import timezone
from rest_framework.exceptions import ValidationError


def future_date_validator(value):
    if value <= timezone.now():
        raise ValidationError("Expected return date should be in the future.")

    if value <= timezone.now() + timezone.timedelta(days=1):
        raise ValidationError("Minimum borrowing term is one day.")

from datetime import datetime, timedelta

from celery import shared_task

from borrowing.models import Borrowing
from notifications.telegram_notifications import (send_no_overdue_notification,
                                                  send_overdue_notification)


@shared_task
def check_overdue_borrowings():
    tomorrow = datetime.now().date() + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow,
        actual_return_date__isnull=True,
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            send_overdue_notification(borrowing)
            return "Send overdue borrowing notification"
    else:
        send_no_overdue_notification()
        return "Send no overdue borrowing notification"

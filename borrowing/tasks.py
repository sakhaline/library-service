from datetime import datetime, timedelta

from celery import shared_task

from borrowing.models import Borrowing


@shared_task
def check_overdue_borrowings():
    tomorrow = datetime.now().date() + timedelta(days=1)
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__day__lte=tomorrow,
        actual_return_date__isnull=True,
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            print("borrowings")
            # send_overdue_borrowing_notification(borrowing)
    else:
        # send_no_overdue_borrowing_notification(borrowing)
        print("No borrowing")

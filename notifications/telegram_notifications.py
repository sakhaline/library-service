import datetime
import os

import telegram
from django.contrib.auth import get_user_model
from django.db.migrations import serializer
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from borrowing.models import Borrowing
from user.models import User

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BORROW_PHOTO = (
    "https://www.englishcurrent.com/wp-content/"
    "uploads/2021/02/borrow-money_1200-compressed.jpg"
)
PAYMENT_PHOTO = (
    "https://stg-cdn-wp.themix.org.uk/"
    "uploads/2014/03/i-need-to-borrow-some-money.jpg"
)

BOT = telegram.Bot(TELEGRAM_API_KEY)


def __create_keyboard(ticket_url: str, all_tickets_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎫 THIS ORDER", url=ticket_url),
                InlineKeyboardButton(
                    text="🎟️ ALL ORDERS", url=all_tickets_url
                ),
            ],
        ]
    )


def borrowing_notification(
    user: get_user_model(),
    borrow: Borrowing,
    books_names: list[str],
    all_tickets_url: str,
) -> None:
    if user.first_name and user.last_name:
        name = f"{user.first_name} {user.last_name}"
    else:
        name = user.email

    ticket_url = f"{all_tickets_url}{borrow.id}/"

    context = f"<b>{name}</b> borrowed"
    if books_names:
        book_list = "\n  ●  ".join(books_names)
        book_plural = "books" if len(books_names) > 1 else "book"
        context += (
            f" {len(books_names)} {book_plural}:\n\n  " f"●  {book_list}\n"
        )
    else:
        context += " no books.\n"

    context += (
        f"\n<b>Borrow date:</b><code> "
        f"{borrow.borrow_date.strftime('%d.%m.%Y')}</code>\n"
        f"<b>Expected return date:</b><code> "
        f"{borrow.expected_return_date.strftime('%d.%m.%Y')}</code>\n"
        f"\nCreated<a href='{ticket_url}'> order {borrow.id}.</a>"
    )

    keyboard = __create_keyboard(ticket_url, all_tickets_url)

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=BORROW_PHOTO,
        caption=context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


def payment_notification(
    user: User,
    amount: float,
    ticket_id: int,
    all_tickets_url: str,
) -> None:
    if user.first_name and user.last_name:
        name = f"{user.first_name} {user.last_name}"
    else:
        name = user.email

    ticket_url = all_tickets_url + str(ticket_id) + "/"

    context = (
        f"<b>{name}</b> payed {amount}$ "
        f"for<a href='{ticket_url}'> order {ticket_id}</a>."
    )

    keyboard = __create_keyboard(ticket_url, all_tickets_url)

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=PAYMENT_PHOTO,
        caption=context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )

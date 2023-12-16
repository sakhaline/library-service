import os

import telegram
from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.response import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from django.contrib.auth import get_user_model
from borrowing.models import Borrowing
from service_config.settings import BASE_URL
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
) -> None:
    """
    Send a borrowing notification to Telegram.

    Args:
        user (User): The user who borrowed the books.
        borrow (Borrowing): The borrowing instance representing the order.
        books_names (list): A list of book names borrowed.
    """
    if user.first_name and user.last_name:
        name = f"{user.first_name} {user.last_name}"
    else:
        name = user.email

    all_tickets_url = f"{BASE_URL}{reverse('borrowing:borrowing-list')}"
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
        f"\n<b>Price: </b><code>{borrow.rent_fee}$</code>"
    )

    keyboard = __create_keyboard(ticket_url, all_tickets_url)

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=BORROW_PHOTO,
        caption=context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )
    if user.telegram_chat_id:
        try:
            BOT.sendPhoto(
                chat_id=user.telegram_chat_id,
                photo=BORROW_PHOTO,
                caption=context,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except telegram.error.Unauthorized:
            error = {
                "Error message": "Your notifications are not working! "
                "Chat not initialized!",
                "Borrowings List": f"{all_tickets_url}",
            }
            raise serializers.ValidationError(error)

        except telegram.error.BadRequest:
            user.telegram_chat_id = ""
            user.save()
            error = {
                "Error message": "Your notifications are not working! The "
                "Chat ID is not correct and was removed!",
                "Borrowings List": f"{all_tickets_url}",
            }
            raise serializers.ValidationError(error)

        except Exception as e:
            error = {
                "Error message": e,
                "Borrowings List": f"{all_tickets_url}",
            }
            raise serializers.ValidationError(error)


def payment_notification(
    user: User,
    borrow: Borrowing,
) -> None:
    """
    Send a notification to Telegram if payment was successful.

    Args:
        user (User): The user who borrowed the books.
        borrow (Borrowing): The borrowing instance representing the order.
    """
    all_tickets_url = f"{BASE_URL}{reverse('payment:payment-list')}"
    if user.first_name and user.last_name:
        name = f"{user.first_name} {user.last_name}"
    else:
        name = user.email

    ticket_url = f"{all_tickets_url}{borrow.id}/"

    context = (
        f"<b>{name}</b> payed {borrow.rent_fee}$ rent "
        f"for<a href='{ticket_url}'> order {borrow.id}</a>."
    )

    keyboard = __create_keyboard(ticket_url, all_tickets_url)

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=PAYMENT_PHOTO,
        caption=context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )

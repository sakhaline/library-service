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


def borrowing_notification(
    user: get_user_model(),
    borrow: Borrowing,
    books_names: list[str],
    payment_url: str = "https://www.python.org/",
) -> None:
    name = (
        f"{user.first_name} {user.last_name}"
        if user.first_name and user.last_name
        else user.email
    )

    all_tickets_url = f"{BASE_URL}{reverse('borrowing:borrowing-list')}"
    ticket_url = f"{all_tickets_url}{borrow.id}/"

    context = f" borrowed"
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

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎫 THIS ORDER", url=ticket_url),
                InlineKeyboardButton(
                    text="🎟️ ALL ORDERS", url=all_tickets_url
                ),
                InlineKeyboardButton(text="💰️ PAY ORDER", url=payment_url),
            ],
        ]
    )

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=BORROW_PHOTO,
        caption=f"<b>{name}</b>" + context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )
    if user.telegram_chat_id:
        try:
            BOT.sendPhoto(
                chat_id=user.telegram_chat_id,
                photo=BORROW_PHOTO,
                caption="<b>You</b>" + context,
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
    name = (
        f"{user.first_name} {user.last_name}"
        if user.first_name and user.last_name
        else user.email
    )

    all_payment_url = f"{BASE_URL}{reverse('payment:payment-list')}"
    payment_url = f"{all_payment_url}{borrow.id}/"

    return_book_url = (
        f"{BASE_URL}{reverse('borrowing:return', args=[borrow.pk])}"
    )

    context = (
        f"\nPayed:  <code>{borrow.rent_fee}$</code>"
        f"\nFor order:  <a href='{payment_url}'><code>{borrow.id}</code></a>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎫 THIS ORDER", url=payment_url),
                InlineKeyboardButton(
                    text="🎟️ ALL ORDERS", url=all_payment_url
                ),
                InlineKeyboardButton(
                    text="📚️ RETURN BOOKS", url=return_book_url
                ),
            ],
        ]
    )

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=BORROW_PHOTO,
        caption=f"<b>{name}</b>" + context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )
    if user.telegram_chat_id:
        try:
            BOT.sendPhoto(
                chat_id=user.telegram_chat_id,
                photo=BORROW_PHOTO,
                caption="<b>You</b>" + context,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except telegram.error.Unauthorized:
            error = {
                "Error message": "Your notifications are not working! "
                "Chat not initialized!",
                "Borrowings List": f"{all_payment_url}",
            }
            raise serializers.ValidationError(error)

        except telegram.error.BadRequest:
            user.telegram_chat_id = ""
            user.save()
            error = {
                "Error message": "Your notifications are not working! The "
                "Chat ID is not correct and was removed!",
                "Borrowings List": f"{all_payment_url}",
            }
            raise serializers.ValidationError(error)

        except Exception as e:
            error = {
                "Error message": e,
                "Borrowings List": f"{all_payment_url}",
            }
            raise serializers.ValidationError(error)

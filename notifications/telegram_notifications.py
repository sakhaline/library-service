import os

import telegram
from django.urls import reverse
from rest_framework import serializers
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from django.contrib.auth import get_user_model
from borrowing.models import Borrowing
from service_config.settings import BASE_URL
from user.models import User

TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BORROW_PHOTO = "https://i.ibb.co/FhgwH3s/Borrowing.png"
PAYMENT_PHOTO = "https://i.ibb.co/pvQKBcL/PAYMENT.jpg"

BOT = telegram.Bot(TELEGRAM_API_KEY)


def format_user_name(user):
    return (
        f"{user.first_name} {user.last_name}"
        if user.first_name and user.last_name
        else user.email
    )


def create_keyboard(single_url, multiple_url, borrow_id, payment_url=None):
    return_book_url = (
        f"{BASE_URL}{reverse('borrowing:return', args=[borrow_id])}"
    )
    if payment_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎫 THIS ORDER", url=single_url),
                    InlineKeyboardButton(
                        text="🎟️ ALL ORDERS", url=multiple_url
                    ),
                ],
                [
                    InlineKeyboardButton(text="💰️ PAY ORDER", url=payment_url),
                    InlineKeyboardButton(
                        text="📚️ RETURN BOOKS", url=return_book_url
                    ),
                ],
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🎫 THIS ORDER", url=single_url),
                    InlineKeyboardButton(
                        text="🎟️ ALL ORDERS", url=multiple_url
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="📚️ RETURN BOOKS", url=return_book_url
                    ),
                ],
            ]
        )


def send_notification(user, photo, context, keyboard, back_url):
    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=photo,
        caption=f"<b>{format_user_name(user)}</b>" + context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )
    if user.telegram_chat_id:
        try:
            BOT.sendPhoto(
                chat_id=user.telegram_chat_id,
                photo=photo,
                caption=f"<b>{format_user_name(user)}</b>" + context,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except telegram.error.Unauthorized:
            user.telegram_chat_id = ""
            user.save()
            error = {
                "Error message": "Your notifications are not working! "
                "Chat not initialized and Chat ID was removed!",
                "Back": f"{back_url}",
            }
            raise serializers.ValidationError(error)

        except telegram.error.BadRequest:
            user.telegram_chat_id = ""
            user.save()
            error = {
                "Error message": "Your notifications are not working! The "
                "Chat ID is not correct and was removed!",
                "Back": f"{back_url}",
            }
            raise serializers.ValidationError(error)

        except Exception as e:
            user.telegram_chat_id = ""
            user.save()
            error = {
                "Error message": e,
                "Back": f"{back_url}",
            }
            raise serializers.ValidationError(error)


def borrowing_notification(
    user: get_user_model(),
    borrow: Borrowing,
    books_names: list[str],
    payment_url: str = "https://www.python.org/",
) -> None:
    all_tickets_url = f"{BASE_URL}{reverse('borrowing:borrowing-list')}"
    ticket_url = f"{all_tickets_url}{borrow.id}/"

    context = " borrowed"
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

    send_notification(
        user=user,
        photo=BORROW_PHOTO,
        context=context,
        keyboard=create_keyboard(
            single_url=ticket_url,
            multiple_url=all_tickets_url,
            payment_url=payment_url,
            borrow_id=borrow.pk,
        ),
        back_url=all_tickets_url,
    )


def payment_notification(
    user: User,
    borrow: Borrowing,
) -> None:
    all_payment_url = f"{BASE_URL}{reverse('payment:payment-list')}"
    payment_url = f"{all_payment_url}{borrow.id}/"

    context = (
        f"\nPayed:  <code>{borrow.rent_fee}$</code>"
        f"\nFor order:  <code>{borrow.id}</code></a>"
    )

    send_notification(
        user=user,
        photo=PAYMENT_PHOTO,
        context=context,
        keyboard=create_keyboard(
            single_url=payment_url,
            multiple_url=all_payment_url,
            borrow_id=borrow.pk,
        ),
        back_url=all_payment_url,
    )

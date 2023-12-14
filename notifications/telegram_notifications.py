import datetime
import os

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

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
    user_first_name: str,
    user_last_name: str,
    books: list[str],
    borrow_date: datetime,
    expected_return_date: datetime,
    ticket_id: int,
    all_tickets_url: str,
) -> None:
    """
    Sends a borrowing notification to a Telegram chat.

    Parameters:
    - user_first_name (str): The first name of the user borrowing.
    - user_last_name (str): The last name of the user borrowing.
    - books (List[str]): A list of books borrowed.
    - borrow_date (datetime): The date when the borrowing took place.
    - expected_return_date (datetime): The date for returning the item.
    - ticket_id (int): The unique identifier for the borrowing order.
    - all_tickets_url (str): The base URL for viewing all borrowing orders.
    """
    ticket_url = all_tickets_url + str(ticket_id) + "/"

    context = f"<b>{user_first_name} {user_last_name}</b> borrowed"
    if books:
        book_list = "\n  ●  ".join(books)
        book_plural = "books" if len(books) > 1 else "book"
        context += f" {len(books)} {book_plural}:\n\n  " f"●  {book_list}\n"
    else:
        context += " no books.\n"

    context += (
        f"\n<b>Borrow date:</b><code> "
        f"{borrow_date.strftime('%d.%m.%Y')}</code>\n"
        f"<b>Expected return date:</b><code> "
        f"{expected_return_date.strftime('%d.%m.%Y')}</code>\n"
        f"\nCreated<a href='{ticket_url}'> order {ticket_id}.</a>"
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
    user_first_name: str,
    user_last_name: str,
    amount: float,
    ticket_id: int,
    all_tickets_url: str,
) -> None:
    """
    Sends a payment notification to a Telegram chat.

    Parameters:
    - user_first_name (str): The first name of the user making the payment.
    - user_last_name (str): The last name of the user making the payment.
    - amount (float): The amount paid by the user.
    - ticket_id (int): The unique identifier for the payment order.
    - all_tickets_url (str): The base URL for viewing all payment orders.
    """
    ticket_url = all_tickets_url + str(ticket_id) + "/"

    context = (
        f"<b>{user_first_name} {user_last_name}</b> payed {amount}$ "
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

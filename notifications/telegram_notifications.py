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


def borrowing_notification(
    user_first_name: str,
    user_last_name: str,
    books: list[str],
    borrow_date: datetime,
    expected_return_date: datetime,
    ticket_id: int,
    all_tickets_url: str,
) -> None:
    ticket_url = all_tickets_url + str(ticket_id) + "/"

    context = f"<b>{user_first_name} {user_last_name}</b> borrowed"
    if books:
        book_list = "\n  ●  ".join(books)
        context += (
            f" {'a few books' if len(books) > 1 else 'a book'}:\n\n  "
            f"●  {book_list}\n"
        )
    else:
        context += " no books.\n"
    context += (
        f"\n<b>Borrow date:</b><code> "
        f"{borrow_date.strftime('%d.%m.%Y')}</code>\n"
        f"<b>Expected return date:</b><code>"
        f" {expected_return_date.strftime('%d.%m.%Y')}</code>\n"
        f"\nCreated<a href='{ticket_url}'> order {ticket_id}.</a>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎫 THIS ORDER", url=ticket_url
                ),
                InlineKeyboardButton(
                    text="🎟️ ALL ORDERS", url=all_tickets_url
                ),
            ],
        ]
    )

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
    ticket_url = all_tickets_url + str(ticket_id) + "/"

    context = (
        f"<b>{user_first_name} {user_last_name}</b> payed {amount}$ "
        f"for<a href='{ticket_url}'> order {ticket_id}</a>."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎫 THIS ORDER", url=ticket_url
                ),
                InlineKeyboardButton(
                    text="🎟️ ALL ORDERS", url=all_tickets_url
                ),
            ],
        ]
    )

    BOT.sendPhoto(
        chat_id=TELEGRAM_CHAT_ID,
        photo=PAYMENT_PHOTO,
        caption=context,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# borrowing_notification(
#     user_first_name="Dmytro",
#     user_last_name="Petrykiv",
#     books=["Clean Code", "Mein Kampf", "How i find your mom"],
#     borrow_date=datetime.date(2023, 12, 14),
#     expected_return_date=datetime.date(2023, 12, 21),
#     ticket_id=1,
#     all_tickets_url="https://chat.openai.com/",
# )
#
# payment_notification(
#     user_first_name="Dmytro",
#     user_last_name="Petrykiv",
#     amount=14.99,
#     ticket_id=1,
#     all_tickets_url="https://chat.openai.com/",
# )

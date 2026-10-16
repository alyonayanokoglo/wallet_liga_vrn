"""Главное меню участника — постоянная reply-клавиатура внизу чата."""

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

CLIENT_NAV_KARMA = "Все активности"
CLIENT_NAV_OFFICE_MAP = "Карта офиса"
CLIENT_NAV_BALANCE = "Мой баланс"
CLIENT_NAV_SPEND = "Списать карму"
CLIENT_NAV_DEMO_PROGRAM = "Программа демо-дня"
CLIENT_NAV_OPEN_MIC = "Задать вопрос на открытый микрофон"
CLIENT_NAV_SNACK = "Где сегодня перекусить?"

CLIENT_NAV_MERCH = "Магазин мерча"
CLIENT_NAV_QUIZ = "Квиз о банке"
CLIENT_NAV_HH = "Поддержи Совкомбанк в рейтинге hh.ru"

CLIENT_NAV_ITEMS = (
    CLIENT_NAV_KARMA,
    CLIENT_NAV_BALANCE,
    CLIENT_NAV_MERCH,
    CLIENT_NAV_QUIZ,
    CLIENT_NAV_DEMO_PROGRAM,
    CLIENT_NAV_OPEN_MIC,
    CLIENT_NAV_OFFICE_MAP,
    CLIENT_NAV_HH,
)
CLIENT_NAV_TEXTS: frozenset[str] = frozenset(CLIENT_NAV_ITEMS)


def strip_reply_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def client_main_nav_reply_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура постоянно видна внизу чата участника."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label)] for label in CLIENT_NAV_ITEMS],
        resize_keyboard=True,
        is_persistent=True,
    )

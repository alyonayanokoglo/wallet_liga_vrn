from collections.abc import Awaitable, Callable
from typing import Optional
from pathlib import Path

from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from client_nav import CLIENT_NAV_OPEN_MIC
from quiz_handlers import QUIZ_INTRO_MEGAPHONE_CUSTOM_EMOJI_ID

GetUserByTelegramId = Callable[[int], Awaitable[Optional[dict]]]
MainNavMarkup = Callable[[], ReplyKeyboardMarkup]

OPEN_MIC_FORM_BUTTON = "Задать вопрос"

OPEN_MIC_PROMPT_HTML = (
    f"<b>Стендап у кулера от Игнатия Винтурова</b> "
    f'<tg-emoji emoji-id="{QUIZ_INTRO_MEGAPHONE_CUSTOM_EMOJI_ID}">📣</tg-emoji>\n\n'
    "<b>20:00–21:30</b>\n\n"
    "На открытом микрофоне разгоним самые животрепещущие карьерные темы.\n\n"
    "<b>Игнатий Винтуров</b> — артист, блогер, музыкальный исполнитель\n"
    "<b>Валерия Козинец</b> — руководитель направления спецпроектов и организации мероприятий Совкомбанка\n"
    "<b>Андрей Пыринов</b> — концептолог и арт-директор Воронежа\n"
    "<b>Никита Татаринский</b> — основатель сети «Культурно Коротко»\n\n"
    "Хочешь задать вопрос? Отправь его через форму — так он точно дойдёт до модераторов."
)


def _open_mic_form_inline_kb(open_mic_form_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=OPEN_MIC_FORM_BUTTON,
                    url=open_mic_form_url,
                ),
            ],
        ]
    )


async def answer_open_mic_prompt(
    message: Message,
    *,
    get_user_by_telegram_id: GetUserByTelegramId,
    main_nav_markup: MainNavMarkup,
    open_mic_form_url: str,
    from_user_id: Optional[int] = None,
) -> None:
    uid = from_user_id or (message.from_user.id if message.from_user else None)
    if uid is None:
        return
    user = await get_user_by_telegram_id(uid)
    if not user:
        await message.answer("Сначала нажми /start и зарегистрируйся.")
        return

    if not open_mic_form_url:
        await message.answer(
            "Форма для вопросов к открытому микрофону пока не подключена. "
            "Подойди к организатору мероприятия.",
            reply_markup=main_nav_markup(),
        )
        return

    await message.answer_photo(
        FSInputFile(str(Path(__file__).resolve().parent / "img" / "open_mic_schedule.png")),
        caption=OPEN_MIC_PROMPT_HTML,
        parse_mode="HTML",
        reply_markup=_open_mic_form_inline_kb(open_mic_form_url),
    )


def register_questions_handlers(
    dp: Dispatcher,
    main_nav_markup: MainNavMarkup,
    get_user_by_telegram_id: GetUserByTelegramId,
    open_mic_form_url: str,
) -> None:
    @dp.message(F.text == CLIENT_NAV_OPEN_MIC)
    async def open_mic_nav(message: Message, state: FSMContext) -> None:
        if message.from_user is None:
            return
        await state.clear()
        await answer_open_mic_prompt(
            message,
            get_user_by_telegram_id=get_user_by_telegram_id,
            main_nav_markup=main_nav_markup,
            open_mic_form_url=open_mic_form_url,
            from_user_id=message.from_user.id,
        )

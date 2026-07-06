from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.messages import t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_language = "es"

    keyboard = [
        [
            InlineKeyboardButton(
                t("create_report", user_language),
                callback_data="create_report",
            )
        ],
        [
            InlineKeyboardButton(
                t("search_report", user_language),
                callback_data="search_report",
            )
        ],
        [
            InlineKeyboardButton(
                t("language", user_language),
                callback_data="language",
            )
        ],
        [
            InlineKeyboardButton(
                t("help", user_language),
                callback_data="help",
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"{t('welcome_title', user_language)}\n\n"
        f"{t('welcome_message', user_language)}\n\n"
        f"{t('main_menu_question', user_language)}"
    )

    if update.message:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
        )

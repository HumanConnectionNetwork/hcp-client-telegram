from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.messages import t


async def create_record_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    user_language = "es"

    keyboard = [
        [InlineKeyboardButton("👤 Persona", callback_data="subject_human")],
        [InlineKeyboardButton("🐾 Animal", callback_data="subject_animal")],
        [InlineKeyboardButton("🚑 Emergencia pública", callback_data="event_public_emergency")],
        [InlineKeyboardButton(t("common.cancel", user_language), callback_data="cancel")],
    ]

    message = (
        f"{t('record.title', user_language)}\n\n"
        "¿Qué tipo de ser vivo deseas reportar?"
    )

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_subject_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    subject_type = query.data.replace("subject_", "")
    context.user_data.clear()
    context.user_data["subject_type"] = subject_type

    user_language = "es"

    if subject_type == "human":
        keyboard = [
            [InlineKeyboardButton(t("event.missing", user_language), callback_data="event_missing")],
            [InlineKeyboardButton(t("event.hospitalized", user_language), callback_data="event_hospitalized")],
            [InlineKeyboardButton(t("event.sheltered", user_language), callback_data="event_sheltered")],
            [InlineKeyboardButton(t("event.safe", user_language), callback_data="event_safe")],
            [InlineKeyboardButton(t("common.cancel", user_language), callback_data="cancel")],
        ]

        message = "👤 Persona\n\n¿Qué deseas reportar?"

    else:
        keyboard = [
            [InlineKeyboardButton("🐾 Animal desaparecido", callback_data="event_missing")],
            [InlineKeyboardButton("🏥 Animal atendido", callback_data="event_hospitalized")],
            [InlineKeyboardButton("🏠 Animal resguardado", callback_data="event_sheltered")],
            [InlineKeyboardButton("✅ Animal localizado / seguro", callback_data="event_safe")],
            [InlineKeyboardButton(t("common.cancel", user_language), callback_data="cancel")],
        ]

        message = "🐾 Animal\n\n¿Qué deseas reportar?"

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

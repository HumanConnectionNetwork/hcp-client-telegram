from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.messages import t


async def create_record_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query:
        await query.answer()

    user_language = "es"

    keyboard = [
        [InlineKeyboardButton(t("event.missing", user_language), callback_data="event_missing")],
        [InlineKeyboardButton(t("event.hospitalized", user_language), callback_data="event_hospitalized")],
        [InlineKeyboardButton(t("event.sheltered", user_language), callback_data="event_sheltered")],
        [InlineKeyboardButton(t("event.safe", user_language), callback_data="event_safe")],
        [InlineKeyboardButton(t("event.public_emergency", user_language), callback_data="event_public_emergency")],
        [InlineKeyboardButton(t("common.cancel", user_language), callback_data="cancel")],
    ]

    await query.edit_message_text(
        text=f"{t('record.title', user_language)}\n\n{t('record.question', user_language)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def ask_estimated_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query:
        await query.answer()

        event_type = query.data.replace("event_", "")
        context.user_data.clear()
        context.user_data["event_type"] = event_type
        context.user_data["record_step"] = "estimated_age"

        print(f"Selected event_type: {event_type}")

        await query.edit_message_text(
            text=(
                "🎂 ¿Cuál es la edad estimada de la persona?\n\n"
                "Puedes escribir un número o una aproximación.\n\n"
                "Ejemplos:\n"
                "34\n"
                "Alrededor de 50\n"
                "Niño\n"
                "Adulto\n"
                "Desconocido"
            )
        )


async def handle_record_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    text = update.message.text.strip()
    current_step = context.user_data.get("record_step")

    if current_step == "estimated_age":
        context.user_data["estimated_age"] = text
        context.user_data["record_step"] = "reported_name"

        await update.message.reply_text(
            "👤 ¿Sabes cómo fue reportada la persona?\n\n"
            "Escribe el nombre reportado o escribe:\n"
            "Desconocido"
        )
        return

    if current_step == "reported_name":
        context.user_data["reported_name"] = text
        context.user_data["record_step"] = "reported_location"

        await update.message.reply_text(
            "📍 ¿Dónde fue reportado el caso?\n\n"
            "Puedes escribir ciudad, barrio, hospital, refugio o punto de referencia."
        )
        return

    if current_step == "reported_location":
        context.user_data["reported_location"] = text
        context.user_data["record_step"] = "source"

        await update.message.reply_text(
            "🏥 ¿Cuál es la fuente de información?\n\n"
            "Ejemplos:\n"
            "Familia\n"
            "Hospital\n"
            "Bomberos\n"
            "Voluntario\n"
            "Policía\n"
            "Desconocido"
        )
        return

    if current_step == "source":
        context.user_data["source"] = text
        context.user_data["record_step"] = "description"

        await update.message.reply_text(
            "📝 Describe brevemente la situación.\n\n"
            "Escribe solo información útil y concreta."
        )
        return

    if current_step == "description":
        context.user_data["description"] = text
        context.user_data["record_step"] = "review"

        summary = (
            "📋 Resumen del reporte\n\n"
            f"Tipo de evento: {context.user_data.get('event_type')}\n"
            f"Edad estimada: {context.user_data.get('estimated_age')}\n"
            f"Nombre reportado: {context.user_data.get('reported_name')}\n"
            f"Lugar reportado: {context.user_data.get('reported_location')}\n"
            f"Fuente: {context.user_data.get('source')}\n"
            f"Descripción: {context.user_data.get('description')}"
        )

        await update.message.reply_text(summary)
        return

from telegram import Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.conversation.search_record.results import show_mock_search_results


async def ask_search_estimated_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    event_type = query.data.replace("search_", "")

    context.user_data.clear()
    context.user_data["search_event_type"] = event_type
    context.user_data["search_step"] = states.ESTIMATED_AGE

    await query.edit_message_text(
        text=(
            "🎂 ¿Qué edad aproximada tiene la persona que buscas?\n\n"
            "Puedes escribir un número o una aproximación.\n\n"
            "Ejemplos:\n"
            "34\n"
            "Alrededor de 50\n"
            "Niño\n"
            "Adulto\n"
            "Desconocido"
        )
    )


async def handle_search_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    text = update.message.text.strip()
    step = context.user_data.get("search_step")

    if step == states.ESTIMATED_AGE:
        context.user_data["search_estimated_age"] = text
        context.user_data["search_step"] = states.REPORTED_NAME

        await update.message.reply_text(
            "👤 ¿Sabes el nombre reportado?\n\n"
            "Si lo sabes, escríbelo.\n"
            "Si no lo sabes, escribe:\n\n"
            "Desconocido"
        )
        return

    if step == states.REPORTED_NAME:
        context.user_data["search_reported_name"] = text
        context.user_data["search_step"] = states.REPORTED_LOCATION

        await update.message.reply_text(
            "📍 ¿En qué localización fue reportada esa persona?\n\n"
            "Puedes escribir ciudad, barrio, hospital, refugio o punto de referencia."
        )
        return

    if step == states.REPORTED_LOCATION:
        context.user_data["search_reported_location"] = text
        context.user_data["search_step"] = states.REVIEW

        await show_mock_search_results(update, context)
        return

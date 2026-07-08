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
            "Escribe solo números.\n\n"
            "Ejemplo:\n"
            "45"
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
        if not text.isdigit():
            await update.message.reply_text(
                "⚠️ La edad debe ser un número.\n\n"
                "Ejemplo:\n"
                "45"
            )
            return

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
    context.user_data["search_step"] = states.RECOGNITION_FEATURES
    await update.message.reply_text(
    "🆔 Características de identificación\n\n"
    "Describe la vestimenta o cualquier característica visible que recuerdes.\n\n"
    "Puedes mencionar ropa, colores, lentes, tatuajes, cicatrices, mochila, collar u otros detalles visibles.\n\n"
    "Esta información puede ayudar a encontrar observaciones relacionadas aunque el nombre o la edad sean imprecisos.\n\n"
    "Máximo 300 caracteres."
)
    return

    if step == states.RECOGNITION_FEATURES:
        if len(text) > 300:
            await update.message.reply_text(
                "⚠️ Las características de identificación deben tener máximo 300 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["search_recognition_features"] = text
        context.user_data["search_step"] = states.REVIEW

        await show_mock_search_results(update, context)
        return



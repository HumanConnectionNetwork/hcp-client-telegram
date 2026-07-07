from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states


async def ask_estimated_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    event_type = query.data.replace("event_", "")

    context.user_data.clear()
    context.user_data["event_type"] = event_type
    context.user_data["record_step"] = states.ESTIMATED_AGE

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


async def ask_reporter_source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    keyboard = [
        [InlineKeyboardButton("👨‍👩‍👧 Familia", callback_data="source_family")],
        [InlineKeyboardButton("🏥 Hospital", callback_data="source_hospital")],
        [InlineKeyboardButton("🚒 Bomberos", callback_data="source_fire_department")],
        [InlineKeyboardButton("🤝 Voluntario", callback_data="source_volunteer")],
        [InlineKeyboardButton("👮 Policía", callback_data="source_police")],
        [InlineKeyboardButton("👤 Amigo / Conocido", callback_data="source_friend")],
        [InlineKeyboardButton("❓ Desconocido", callback_data="source_unknown")],
    ]

    await update.message.reply_text(
        "📣 ¿Quién está reportando este evento?\n\n"
        "Selecciona la opción que mejor describa la fuente del reporte.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_reporter_source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    source = query.data.replace("source_", "")

    context.user_data["source"] = source
    context.user_data["record_step"] = states.DESCRIPTION

    await query.edit_message_text(
        text=(
            "📝 Describe brevemente la situación.\n\n"
            "Escribe únicamente información útil y relevante."
        )
    )


async def handle_record_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    text = update.message.text.strip()
    step = context.user_data.get("record_step")

    if step == states.ESTIMATED_AGE:
        context.user_data["estimated_age"] = text
        context.user_data["record_step"] = states.REPORTED_NAME

        await update.message.reply_text(
            "👤 ¿Sabes el nombre de la persona?\n\n"
            "Si lo sabes, escribe el nombre reportado.\n"
            "Si no lo sabes, escribe:\n\n"
            "Desconocido"
        )
        return

    if step == states.REPORTED_NAME:
        context.user_data["reported_name"] = text
        context.user_data["record_step"] = states.REPORTED_LOCATION

        await update.message.reply_text(
            "📍 ¿En qué localización está esa persona?\n\n"
            "Puedes escribir:\n"
            "- Ciudad\n"
            "- Barrio\n"
            "- Hospital\n"
            "- Refugio\n"
            "- Punto de referencia"
        )
        return

    if step == states.REPORTED_LOCATION:
        context.user_data["reported_location"] = text
        context.user_data["record_step"] = states.SOURCE

        await ask_reporter_source(update, context)
        return

    if step == states.DESCRIPTION:
        context.user_data["description"] = text
        context.user_data["record_step"] = states.REVIEW

        await update.message.reply_text(
            "✅ Información recibida.\n\n"
            "En el siguiente paso podrás revisar el reporte antes de enviarlo."
        )
        return

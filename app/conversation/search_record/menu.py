from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.messages import t


async def search_record_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Displays the initial Search Record menu.

    Search does not ask for the observation type because the user may not
    know how the case was originally reported. The HCP node should correlate
    compatible observations across event types.
    """

    query = update.callback_query

    if not query:
        return

    await query.answer()

    user_language = "es"

    keyboard = [
        [
            InlineKeyboardButton(
                "👤 Buscar persona",
                callback_data="search_person",
            )
        ],
        [
            InlineKeyboardButton(
                "🐾 Buscar animal",
                callback_data="search_animal",
            )
        ],
        [
            InlineKeyboardButton(
                t("common.cancel", user_language),
                callback_data="cancel",
            )
        ],
    ]

    message = (
        "🔍 Buscar caso reportado\n\n"
        "HCP busca observaciones humanitarias, no identidades.\n\n"
        "Cuando varias observaciones describen un mismo caso, "
        "el sistema puede encontrar posibles casos relacionados mediante "
        "un proceso de correlación.\n\n"
        "Puedes comenzar con el nombre y agregar más información "
        "para obtener resultados más precisos.\n\n"
        "¿Qué deseas buscar?"
    )

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

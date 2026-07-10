from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.messages import t


async def create_record_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Displays the first menu for creating a humanitarian report.

    This screen uses natural, action-oriented language. The user does not
    need to understand HCP concepts or internal event classifications.
    """

    query = update.callback_query

    if not query:
        return

    await query.answer()

    user_language = "es"

    keyboard = [
        [
            InlineKeyboardButton(
                "👤 Reportar persona",
                callback_data="subject_human",
            )
        ],
        [
            InlineKeyboardButton(
                "🐾 Reportar animal",
                callback_data="subject_animal",
            )
        ],
        [
            InlineKeyboardButton(
                "🚨 Reportar emergencia pública",
                callback_data="event_public_emergency",
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
        f"{t('record.title', user_language)}\n\n"
        "¿Qué deseas reportar?"
    )

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_subject_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Displays the human or animal observation menu.

    Human reports describe the observed situation.

    Animal reports distinguish only between:
    - an animal reported as missing;
    - an animal found or currently under someone's care.
    """

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
            [
                InlineKeyboardButton(
                    "👤 Persona desaparecida",
                    callback_data="event_missing",
                )
            ],
            [
                InlineKeyboardButton(
                    "🏥 Persona hospitalizada",
                    callback_data="event_hospitalized",
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Persona refugiada",
                    callback_data="event_sheltered",
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Persona localizada",
                    callback_data="event_safe",
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
            "👤 Reportar persona\n\n"
            "Selecciona la situación que deseas informar."
        )

    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "🐾 Animal desaparecido",
                    callback_data="event_missing",
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ Animal encontrado",
                    callback_data="event_found",
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
            "🐾 Reportar animal\n\n"
            "¿Qué ocurrió?\n\n"
            "• Si perdiste una mascota o no sabes dónde está, selecciona "
            "«Animal desaparecido».\n\n"
            "• Si encontraste un animal o lo tienes temporalmente bajo tu cuidado, "
            "selecciona «Animal encontrado»."
        )

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

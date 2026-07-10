from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.conversation.create_record.edit import handle_edit_text
from app.conversation.create_record.review import review_record


MAX_NAME_LENGTH = 80
MAX_LOCATION_LENGTH = 120
MAX_RECOGNITION_FEATURES_LENGTH = 300
MAX_PUBLIC_CONTACT_LENGTH = 160
MAX_BREED_LENGTH = 40


ANIMAL_ICONS = {
    "dog": "🐕",
    "cat": "🐈",
    "horse": "🐎",
    "bird": "🦜",
    "unknown": "🐾",
}


async def ask_estimated_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    event_type = query.data.replace("event_", "")
    context.user_data["event_type"] = event_type

    subject_type = context.user_data.get("subject_type", "human")

    if subject_type == "animal":
        context.user_data["record_step"] = states.ANIMAL_SPECIES
        await show_animal_species_options(update, context)
        return

    context.user_data["record_step"] = states.REPORTED_NAME

    await query.edit_message_text(
        text=(
            "👤 ¿Sabes el nombre de la persona?\n\n"
            "Si lo sabes, escribe el nombre reportado.\n\n"
            "Si no lo sabes, escribe:\n"
            "Desconocido"
        )
    )


async def show_animal_species_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    keyboard = [
        [
            InlineKeyboardButton(
                "🐕 Perro",
                callback_data="animal_species_dog",
            )
        ],
        [
            InlineKeyboardButton(
                "🐈 Gato",
                callback_data="animal_species_cat",
            )
        ],
        [
            InlineKeyboardButton(
                "🐎 Caballo",
                callback_data="animal_species_horse",
            )
        ],
        [
            InlineKeyboardButton(
                "🦜 Ave",
                callback_data="animal_species_bird",
            )
        ],
        [
            InlineKeyboardButton(
                "🐾 Otro / No sé",
                callback_data="animal_species_unknown",
            )
        ],
    ]

    if query:
        await query.edit_message_text(
            text="🐾 ¿Qué animal es?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def handle_animal_species(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    species = query.data.replace("animal_species_", "")
    context.user_data["animal_species"] = species
    context.user_data["record_step"] = states.ANIMAL_SIZE

    await show_animal_size_options(update, context)


async def show_animal_size_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    species = context.user_data.get("animal_species", "unknown")
    icon = ANIMAL_ICONS.get(species, "🐾")

    keyboard = [
        [
            InlineKeyboardButton(
                f"{icon} Grande",
                callback_data="animal_size_large",
            )
        ],
        [
            InlineKeyboardButton(
                f"{icon} Mediano",
                callback_data="animal_size_medium",
            )
        ],
        [
            InlineKeyboardButton(
                f"{icon} Pequeño",
                callback_data="animal_size_small",
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Desconocido",
                callback_data="animal_size_unknown",
            )
        ],
    ]

    if query:
        await query.edit_message_text(
            text=f"{icon} ¿Cuál es el tamaño aproximado del animal?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def handle_animal_size(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    size = query.data.replace("animal_size_", "")
    context.user_data["animal_size"] = size
    context.user_data["record_step"] = states.ANIMAL_BREED_TYPE

    await show_animal_breed_options(update, context)


async def show_animal_breed_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    species = context.user_data.get("animal_species", "unknown")
    icon = ANIMAL_ICONS.get(species, "🐾")

    keyboard = [
        [
            InlineKeyboardButton(
                f"{icon} Raza / especie conocida",
                callback_data="animal_breed_known",
            )
        ],
        [
            InlineKeyboardButton(
                f"{icon} Mestizo / Criollo",
                callback_data="animal_breed_mixed",
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Desconocida",
                callback_data="animal_breed_unknown",
            )
        ],
    ]

    if query:
        await query.edit_message_text(
            text=f"{icon} ¿Qué raza, tipo o especie parece ser?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def handle_animal_breed(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    breed_type = query.data.replace("animal_breed_", "")
    context.user_data["animal_breed_type"] = breed_type

    if breed_type == "known":
        context.user_data["record_step"] = states.ANIMAL_BREED_TEXT

        species = context.user_data.get("animal_species", "unknown")

        breed_examples = {
            "dog": (
                "Rottweiler, Pastor Alemán, Golden Retriever, mestizo"
            ),
            "cat": "Siamés, Angora, Persa, mestizo",
            "horse": "Pura sangre, Criollo, Cuarto de milla",
            "bird": "Loro, Guacamaya, Periquito, Canario",
            "unknown": "Si no lo sabes, escribe: Desconocido",
        }

        species_labels = {
            "dog": "raza aproximada",
            "cat": "raza aproximada",
            "horse": "raza o tipo aproximado",
            "bird": "especie aproximada",
            "unknown": "raza, tipo o especie aproximada",
        }

        example = breed_examples.get(
            species,
            breed_examples["unknown"],
        )
        icon = ANIMAL_ICONS.get(species, "🐾")
        label = species_labels.get(
            species,
            species_labels["unknown"],
        )

        await query.edit_message_text(
            text=(
                f"{icon} Escribe la {label}.\n\n"
                "Máximo 40 caracteres.\n\n"
                f"Ejemplos:\n{example}"
            )
        )
        return

    context.user_data["animal_breed"] = breed_type
    context.user_data["record_step"] = states.REPORTED_NAME

    await query.edit_message_text(
        text=(
            "🐾 ¿Sabes el nombre del animal?\n\n"
            "Si lo sabes, escribe el nombre reportado.\n\n"
            "Si no lo sabes, escribe:\n"
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
        [
            InlineKeyboardButton(
                "👨‍👩‍👧 Familia",
                callback_data="source_family",
            )
        ],
        [
            InlineKeyboardButton(
                "🏥 Hospital",
                callback_data="source_hospital",
            )
        ],
        [
            InlineKeyboardButton(
                "🚒 Bomberos",
                callback_data="source_fire_department",
            )
        ],
        [
            InlineKeyboardButton(
                "🤝 Voluntario",
                callback_data="source_volunteer",
            )
        ],
        [
            InlineKeyboardButton(
                "👮 Policía",
                callback_data="source_police",
            )
        ],
        [
            InlineKeyboardButton(
                "👤 Amigo / Conocido",
                callback_data="source_friend",
            )
        ],
        [
            InlineKeyboardButton(
                "❓ Desconocido",
                callback_data="source_unknown",
            )
        ],
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
    context.user_data["record_step"] = states.RECOGNITION_FEATURES

    subject_type = context.user_data.get("subject_type", "human")

    if subject_type == "animal":
        description = (
            "Describe cualquier característica visible que facilite "
            "reconocer al animal.\n\n"
        )

        examples = (
            "Puedes incluir información como:\n\n"
            "🎨 Color del pelaje\n"
            "⚪ Manchas\n"
            "🦺 Collar o arnés\n"
            "🏷️ Placa identificadora\n"
            "🩹 Cicatrices\n"
            "🐾 Forma de caminar\n"
            "👁️ Color de los ojos"
        )
    else:
        description = (
            "Describe cualquier característica visible que facilite "
            "reconocer a la persona.\n\n"
        )

        examples = (
            "Puedes incluir información como:\n\n"
            "👕 Vestimenta\n"
            "🎨 Colores\n"
            "👓 Lentes\n"
            "🎒 Mochila\n"
            "🖋️ Tatuajes\n"
            "🩹 Cicatrices\n"
            "💇 Cabello"
        )

    await query.edit_message_text(
        text=(
            "🧩 Características para identificación\n\n"
            f"{description}"
            f"{examples}\n\n"
            "Máximo 300 caracteres."
        )
    )


async def ask_public_contact(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Explains the optional public contact field.

    The value is stored with the observation but never used as a
    correlation variable.
    """

    if not update.message:
        return

    await update.message.reply_text(
        text=(
            "📞 Medio de contacto (opcional)\n\n"
            "Human Connection Protocol está diseñado para conectar "
            "observaciones humanitarias sin crear una base de datos central "
            "de personas o contactos.\n\n"
            "Si deseas que otra persona pueda comunicarse contigo acerca de "
            "este caso, puedes compartir un medio de contacto.\n\n"
            "Por ejemplo:\n\n"
            "📱 Número de teléfono\n"
            "💬 Usuario de Telegram\n"
            "📧 Correo electrónico\n\n"
            "Este dato:\n\n"
            "✅ No participa en la correlación del caso.\n"
            "✅ No se utiliza para encontrar personas o animales.\n"
            "✅ No forma parte de una base de datos central de contactos.\n\n"
            "Su único propósito es facilitar que otra persona pueda "
            "comunicarse contigo si cree que encontró información relacionada "
            "con este caso.\n\n"
            "📞 ¿Qué medio de contacto deseas compartir?\n\n"
            "Máximo 160 caracteres."
        )
    )


async def handle_record_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if await handle_edit_text(update, context):
        return

    if not update.message:
        return

    text = update.message.text.strip()
    step = context.user_data.get("record_step")
    subject_type = context.user_data.get("subject_type", "human")

    if step == states.ANIMAL_BREED_TEXT:
        if len(text) > MAX_BREED_LENGTH:
            await update.message.reply_text(
                "⚠️ La raza debe tener máximo 40 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["animal_breed"] = text
        context.user_data["record_step"] = states.REPORTED_NAME

        await update.message.reply_text(
            "🐾 ¿Sabes el nombre del animal?\n\n"
            "Si lo sabes, escribe el nombre reportado.\n\n"
            "Si no lo sabes, escribe:\n"
            "Desconocido"
        )
        return

    if step == states.REPORTED_NAME:
        if len(text) > MAX_NAME_LENGTH:
            await update.message.reply_text(
                "⚠️ El nombre debe tener máximo 80 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["reported_name"] = text

        if subject_type == "animal":
            context.user_data["record_step"] = states.REPORTED_LOCATION

            await update.message.reply_text(
                "📍 ¿Dónde se encuentra o fue visto el animal?\n\n"
                "Puedes escribir ciudad, barrio, refugio, clínica veterinaria "
                "o punto de referencia.\n\n"
                "Máximo 120 caracteres."
            )
            return

        context.user_data["record_step"] = states.ESTIMATED_AGE

        await update.message.reply_text(
            "🎂 ¿Cuál es la edad estimada de la persona?\n\n"
            "Escribe solo números.\n\n"
            "Ejemplo:\n"
            "45"
        )
        return

    if step == states.ESTIMATED_AGE:
        if not text.isdigit():
            await update.message.reply_text(
                "⚠️ La edad debe ser un número.\n\n"
                "Ejemplo:\n"
                "45"
            )
            return

        context.user_data["estimated_age"] = text
        context.user_data["record_step"] = states.REPORTED_LOCATION

        await update.message.reply_text(
            "📍 ¿En qué localización está esa persona?\n\n"
            "Puedes escribir:\n"
            "• Ciudad\n"
            "• Barrio\n"
            "• Hospital\n"
            "• Refugio\n"
            "• Punto de referencia\n\n"
            "Máximo 120 caracteres."
        )
        return

    if step == states.REPORTED_LOCATION:
        if len(text) > MAX_LOCATION_LENGTH:
            await update.message.reply_text(
                "⚠️ La localización debe tener máximo 120 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["reported_location"] = text
        context.user_data["record_step"] = states.SOURCE

        await ask_reporter_source(update, context)
        return

    if step == states.RECOGNITION_FEATURES:
        if len(text) > MAX_RECOGNITION_FEATURES_LENGTH:
            await update.message.reply_text(
                "⚠️ Las características de identificación deben tener "
                "máximo 300 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["recognition_features"] = text
        context.user_data["record_step"] = states.PUBLIC_CONTACT_TEXT

        await ask_public_contact(update, context)
        return

    if step == states.PUBLIC_CONTACT_TEXT:
        if len(text) > MAX_PUBLIC_CONTACT_LENGTH:
            await update.message.reply_text(
                "⚠️ El medio de contacto debe tener máximo "
                "160 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return

        context.user_data["public_contact"] = text
        context.user_data["record_step"] = states.REVIEW

        await review_record(update, context)
        return

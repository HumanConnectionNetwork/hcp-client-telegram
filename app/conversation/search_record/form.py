from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states


ANIMAL_ICONS = {
    "dog": "🐕",
    "cat": "🐈",
    "horse": "🐎",
    "bird": "🦜",
    "other": "🐾",
}


ANIMAL_BREED_EXAMPLES = {
    "dog": "Rottweiler, Pastor Alemán, Golden Retriever, mestizo.",
    "cat": "Siamés, Angora, Persa, mestizo.",
    "horse": "Pura sangre, Criollo, Cuarto de milla.",
    "bird": "Loro, Guacamaya, Periquito, Canario.",
    "other": "Conejo, cabra, tortuga, mono.",
}


def _get_search_data(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "search_record" not in context.user_data:
        context.user_data["search_record"] = {}

    return context.user_data["search_record"]


async def start_person_search_form(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    if not query:
        return states.SEARCH_REPORTED_NAME

    await query.answer()

    search_data = _get_search_data(context)
    search_data.clear()
    search_data["category"] = "person"

    message = (
        "👤 Buscar persona\n\n"
        "Puedes comenzar con el nombre y agregar más información para obtener "
        "posibles casos relacionados con mayor precisión.\n\n"
        "¿Cuál es el nombre de la persona que buscas?"
    )

    await query.edit_message_text(text=message)

    return states.SEARCH_REPORTED_NAME


async def receive_person_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["reported_name"] = update.message.text.strip()

    message = (
        "🔢 Edad aproximada\n\n"
        "Escribe la edad aproximada de la persona usando solo números.\n\n"
        "Ejemplo: 34"
    )

    await update.message.reply_text(message)

    return states.SEARCH_ESTIMATED_AGE


async def receive_person_age(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text(
            "La edad debe ser un número.\n\n"
            "Ejemplo: 34"
        )
        return states.SEARCH_ESTIMATED_AGE

    search_data = _get_search_data(context)
    search_data["estimated_age"] = int(text)

    message = (
        "📍 Ubicación o referencia\n\n"
        "Escribe la ciudad, barrio, hospital, refugio o punto de referencia "
        "que pueda estar relacionado con la búsqueda.\n\n"
        "Ejemplo: Hospital Central de Valencia, Carabobo"
    )

    await update.message.reply_text(message)

    return states.SEARCH_LOCATION


async def receive_person_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["location"] = update.message.text.strip()

    message = (
        "🧩 Características para identificación\n\n"
        "Agrega detalles que puedan ayudar a encontrar observaciones relacionadas.\n\n"
        "Puedes incluir información como:\n\n"
        "👕 Vestimenta\n"
        "🎨 Colores\n"
        "👓 Lentes\n"
        "🎒 Mochila\n"
        "🖋️ Tatuajes\n"
        "🩹 Cicatrices\n"
        "💇 Cabello"
    )

    await update.message.reply_text(message)

    return states.SEARCH_RECOGNITION_FEATURES


async def receive_person_features(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["recognition_features"] = update.message.text.strip()

    return states.SEARCH_RESULTS


async def start_animal_search_form(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    if not query:
        return states.SEARCH_ANIMAL_SPECIES

    await query.answer()

    search_data = _get_search_data(context)
    search_data.clear()
    search_data["category"] = "animal"

    keyboard = [
        [InlineKeyboardButton("🐕 Perro", callback_data="search_animal_species_dog")],
        [InlineKeyboardButton("🐈 Gato", callback_data="search_animal_species_cat")],
        [InlineKeyboardButton("🐎 Caballo", callback_data="search_animal_species_horse")],
        [InlineKeyboardButton("🦜 Ave", callback_data="search_animal_species_bird")],
        [InlineKeyboardButton("🐾 Otro", callback_data="search_animal_species_other")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")],
    ]

    message = (
        "🐾 Buscar animal\n\n"
        "Selecciona la especie o tipo de animal."
    )

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return states.SEARCH_ANIMAL_SPECIES


async def receive_animal_species(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    if not query:
        return states.SEARCH_ANIMAL_SPECIES

    await query.answer()

    species = query.data.replace("search_animal_species_", "")

    search_data = _get_search_data(context)
    search_data["species"] = species

    icon = ANIMAL_ICONS.get(species, "🐾")

    message = (
        f"{icon} Nombre del animal\n\n"
        "¿Cuál es el nombre del animal que buscas?"
    )

    await query.edit_message_text(text=message)

    return states.SEARCH_ANIMAL_NAME


async def receive_animal_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["animal_name"] = update.message.text.strip()

    species = search_data.get("species", "other")
    icon = ANIMAL_ICONS.get(species, "🐾")

    keyboard = [
        [InlineKeyboardButton(f"{icon} Pequeño", callback_data="search_animal_size_small")],
        [InlineKeyboardButton(f"{icon} Mediano", callback_data="search_animal_size_medium")],
        [InlineKeyboardButton(f"{icon} Grande", callback_data="search_animal_size_large")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")],
    ]

    message = (
        f"{icon} Tamaño aproximado\n\n"
        "Selecciona el tamaño aproximado del animal."
    )

    await update.message.reply_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return states.SEARCH_ANIMAL_SIZE


async def receive_animal_size(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    if not query:
        return states.SEARCH_ANIMAL_SIZE

    await query.answer()

    size = query.data.replace("search_animal_size_", "")

    search_data = _get_search_data(context)
    search_data["size"] = size

    species = search_data.get("species", "other")
    icon = ANIMAL_ICONS.get(species, "🐾")
    examples = ANIMAL_BREED_EXAMPLES.get(species, ANIMAL_BREED_EXAMPLES["other"])

    message = (
        f"{icon} Raza, tipo o especie específica\n\n"
        "Escribe la raza, tipo o especie específica del animal.\n\n"
        f"Ejemplos:\n{examples}"
    )

    await query.edit_message_text(text=message)

    return states.SEARCH_ANIMAL_BREED_TEXT


async def receive_animal_breed_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["breed_or_type"] = update.message.text.strip()

    message = (
        "📍 Ubicación o referencia\n\n"
        "Escribe la ciudad, barrio, refugio, clínica veterinaria o punto "
        "de referencia que pueda estar relacionado con la búsqueda."
    )

    await update.message.reply_text(message)

    return states.SEARCH_ANIMAL_LOCATION


async def receive_animal_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["location"] = update.message.text.strip()

    species = search_data.get("species", "other")
    icon = ANIMAL_ICONS.get(species, "🐾")

    message = (
        f"{icon} Características para identificación\n\n"
        "Agrega detalles que puedan ayudar a encontrar observaciones relacionadas.\n\n"
        "Puedes incluir información como:\n\n"
        "🎨 Color del pelaje\n"
        "⚪ Manchas\n"
        "🦺 Collar o arnés\n"
        "🏷️ Placa identificadora\n"
        "🩹 Cicatrices\n"
        "🐾 Forma de caminar\n"
        "👁️ Color de los ojos"
    )

    await update.message.reply_text(message)

    return states.SEARCH_ANIMAL_FEATURES


async def receive_animal_features(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    search_data["recognition_features"] = update.message.text.strip()

    return states.SEARCH_RESULTS

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.messages import t


PERSON_SEARCH_EVENT_TYPES = {
    "search_person_missing": "missing_person",
    "search_person_hospitalized": "hospitalized_person",
    "search_person_sheltered": "sheltered_person",
    "search_person_safe": "safe_person",
}

ANIMAL_SEARCH_EVENT_TYPES = {
    "search_animal_missing": "missing_animal",
    "search_animal_found": "found_animal",
}


ANIMAL_ICONS = {
    "dog": "🐕",
    "cat": "🐈",
    "horse": "🐎",
    "bird": "🦜",
    "other": "🐾",
}


ANIMAL_BREED_EXAMPLES = {
    "dog": "Ejemplos: Rottweiler, Pastor Alemán, mestizo.",
    "cat": "Ejemplos: Siamés, Angora, persa, mestizo.",
    "horse": "Ejemplos: Pura sangre, criollo, cuarto de milla.",
    "bird": "Ejemplos: loro, guacamaya, periquito, lechuza, canario.",
    "other": "Ejemplos: conejo, cabra, tortuga, mono.",
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
    search_data["event_type"] = PERSON_SEARCH_EVENT_TYPES.get(query.data)

    message = (
        "👤 Buscar persona\n\n"
        "Puedes escribir solo el nombre o agregar más información para obtener "
        "resultados más precisos.\n\n"
        "¿Cuál es el nombre reportado de la persona?\n\n"
        "Si no lo sabes, escribe: Desconocido"
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
        "🔢 Edad estimada\n\n"
        "Escribe la edad aproximada de la persona usando solo números.\n\n"
        "Ejemplo: 34\n\n"
        "Si no la sabes, escribe: 0"
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
            "Ejemplo: 34\n\n"
            "Si no la sabes, escribe: 0"
        )
        return states.SEARCH_ESTIMATED_AGE

    search_data = _get_search_data(context)
    search_data["estimated_age"] = int(text)

    message = (
        "📍 Ubicación o referencia\n\n"
        "Escribe la ciudad, barrio, hospital, refugio o punto de referencia "
        "donde podría estar relacionado el caso.\n\n"
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

    user_language = "es"

    keyboard = [
        [InlineKeyboardButton("Familia", callback_data="search_source_family")],
        [InlineKeyboardButton("Hospital", callback_data="search_source_hospital")],
        [InlineKeyboardButton("Bomberos", callback_data="search_source_firefighters")],
        [InlineKeyboardButton("Voluntario", callback_data="search_source_volunteer")],
        [InlineKeyboardButton("Policía", callback_data="search_source_police")],
        [InlineKeyboardButton("Amigo/Conocido", callback_data="search_source_friend")],
        [InlineKeyboardButton("Desconocido", callback_data="search_source_unknown")],
        [InlineKeyboardButton(t("common.cancel", user_language), callback_data="cancel")],
    ]

    message = (
        "👥 Relación o fuente\n\n"
        "Selecciona quién reportó o podría haber observado este caso."
    )

    await update.message.reply_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return states.SEARCH_SOURCE


async def receive_person_source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    query = update.callback_query

    if not query:
        return states.SEARCH_SOURCE

    await query.answer()

    source_map = {
        "search_source_family": "family",
        "search_source_hospital": "hospital",
        "search_source_firefighters": "firefighters",
        "search_source_volunteer": "volunteer",
        "search_source_police": "police",
        "search_source_friend": "friend",
        "search_source_unknown": "unknown",
    }

    search_data = _get_search_data(context)
    search_data["source"] = source_map.get(query.data, "unknown")

    message = (
        "🧩 Características para identificación\n\n"
        "Agrega detalles que puedan ayudar a encontrar registros relacionados.\n\n"
        "Ejemplos: ropa, lentes, tatuajes, cicatrices, color de cabello, "
        "estatura aproximada.\n\n"
        "Si no tienes más información, escribe: Omitir"
    )

    await query.edit_message_text(text=message)

    return states.SEARCH_RECOGNITION_FEATURES


async def receive_person_features(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    text = update.message.text.strip()

    search_data["recognition_features"] = "" if text.lower() == "omitir" else text

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
    search_data["event_type"] = ANIMAL_SEARCH_EVENT_TYPES.get(query.data)

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
        "Escribe el nombre del animal, si lo conoces.\n\n"
        "Si no lo sabes, escribe: Desconocido"
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
        f"{examples}\n\n"
        "Escribe la raza, tipo o especie específica.\n\n"
        "Si no lo sabes, escribe: Desconocido"
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
        "de referencia donde podría estar relacionado el caso."
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
        "Agrega detalles que ayuden a reconocer al animal.\n\n"
        "Ejemplos: color, manchas, collar, heridas visibles, comportamiento, "
        "señas particulares.\n\n"
        "Si no tienes más información, escribe: Omitir"
    )

    await update.message.reply_text(message)

    return states.SEARCH_ANIMAL_FEATURES


async def receive_animal_features(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    search_data = _get_search_data(context)
    text = update.message.text.strip()

    search_data["recognition_features"] = "" if text.lower() == "omitir" else text

    return states.SEARCH_RESULTS

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.search.correlation import correlate_records
from app.storage.hcp_storage import load_records


CONTACT_VISIBILITY_THRESHOLD = 60


EVENT_TYPE_LABELS = {
    "missing_person": "🚨 Persona desaparecida",
    "hospitalized_person": "🏥 Persona hospitalizada",
    "sheltered_person": "🏠 Persona refugiada",
    "safe_person": "✅ Persona localizada",
    "missing_animal": "🐾 Animal desaparecido",
    "found_animal": "✅ Animal encontrado",
}


SOURCE_LABELS = {
    "family": "👨‍👩‍👧 Familia",
    "hospital": "🏥 Hospital",
    "fire_department": "🚒 Bomberos",
    "volunteer": "🤝 Voluntario",
    "police": "👮 Policía",
    "friend": "👤 Amigo / Conocido",
    "unknown": "❓ Desconocido",
}


ANIMAL_SPECIES_LABELS = {
    "dog": "Perro",
    "cat": "Gato",
    "horse": "Caballo",
    "bird": "Ave",
    "other": "Otro",
    "unknown": "Animal",
}


ANIMAL_SIZE_LABELS = {
    "small": "Pequeño",
    "medium": "Mediano",
    "large": "Grande",
    "unknown": "Desconocido",
}


def _format_unknown(value: object) -> str:
    """
    Returns a human-readable value for missing or empty data.
    """

    if value is None:
        return "No especificado"

    text = str(value).strip()

    if not text or text == "0":
        return "No especificado"

    return text


def _event_type_label(value: object) -> str:
    """
    Converts a canonical event type into a human-readable label.
    """

    key = str(value or "").strip()

    return EVENT_TYPE_LABELS.get(
        key,
        _format_unknown(value),
    )


def _source_label(value: object) -> str:
    """
    Converts a canonical source value into a human-readable label.
    """

    key = str(value or "").strip()

    return SOURCE_LABELS.get(
        key,
        _format_unknown(value),
    )


def _animal_species_label(value: object) -> str:
    """
    Converts the canonical animal species value into Spanish.
    """

    key = str(value or "").strip()

    return ANIMAL_SPECIES_LABELS.get(
        key,
        _format_unknown(value),
    )


def _animal_size_label(value: object) -> str:
    """
    Converts the canonical animal size value into Spanish.
    """

    key = str(value or "").strip()

    return ANIMAL_SIZE_LABELS.get(
        key,
        _format_unknown(value),
    )


def _candidate_callback_id(candidate: dict) -> str:
    """
    Returns a safe callback identifier for Telegram.

    Telegram callback_data has a limited size, so the UUID is truncated
    defensively even though current UUIDs already fit.
    """

    candidate_id = str(
        candidate.get("candidate_id", "unknown")
    )

    return candidate_id[:60]


def _store_candidate_explanations(
    context: ContextTypes.DEFAULT_TYPE,
    candidates: list[dict],
) -> None:
    """
    Stores real correlation explanations temporarily for explain.py.
    """

    explanations = {}

    for candidate in candidates:
        candidate_id = _candidate_callback_id(candidate)

        explanations[candidate_id] = {
            "probability": candidate.get("probability", 0),
            "matches": candidate.get("matches", []),
            "warnings": candidate.get("warnings", []),
            "record": candidate.get("record", {}),
        }

    context.user_data["search_explanations"] = explanations


def _format_search_summary(search_data: dict) -> str:
    """
    Formats the information entered by the user during the search.
    """

    category = search_data.get("category", "person")

    if category == "animal":
        return (
            f"🐾 Animal: "
            f"{_animal_species_label(search_data.get('species'))}\n"
            f"🏷️ Nombre: "
            f"{_format_unknown(search_data.get('animal_name'))}\n"
            f"📏 Tamaño: "
            f"{_animal_size_label(search_data.get('size'))}\n"
            f"🧬 Raza / tipo: "
            f"{_format_unknown(search_data.get('breed_or_type'))}\n"
            f"📍 Ubicación: "
            f"{_format_unknown(search_data.get('location'))}\n"
            f"🧩 Características: "
            f"{_format_unknown(search_data.get('recognition_features'))}\n\n"
        )

    return (
        f"👤 Nombre: "
        f"{_format_unknown(search_data.get('reported_name'))}\n"
        f"🎂 Edad aproximada: "
        f"{_format_unknown(search_data.get('estimated_age'))}\n"
        f"📍 Ubicación: "
        f"{_format_unknown(search_data.get('location'))}\n"
        f"🧩 Características: "
        f"{_format_unknown(search_data.get('recognition_features'))}\n\n"
    )


def _should_show_public_contact(
    candidate: dict,
    record: dict,
) -> bool:
    """
    Determines whether the public contact may be displayed.

    The contact is visible only when:
    - the record contains a public contact;
    - the correlation probability reaches the configured threshold.

    The contact itself never contributes to the correlation score.
    """

    probability = int(
        candidate.get("probability", 0)
    )
    public_contact = str(
        record.get("public_contact") or ""
    ).strip()

    return (
        probability >= CONTACT_VISIBILITY_THRESHOLD
        and bool(public_contact)
    )


def _format_candidate(
    index: int,
    candidate: dict,
) -> str:
    """
    Formats one real HCP correlation candidate.
    """

    record = candidate.get("record", {})
    subject_type = record.get("subject_type", "human")
    probability = int(
        candidate.get("probability", 0)
    )

    base = (
        "──────────────\n"
        f"📄 Posible caso relacionado #{index}\n\n"
        f"Probabilidad: {probability}%\n"
        f"Tipo: {_event_type_label(record.get('event_type'))}\n"
        f"Estado: {_format_unknown(record.get('status'))}\n"
        f"Fuente: {_source_label(record.get('source'))}\n\n"
        f"Nombre reportado: "
        f"{_format_unknown(record.get('reported_name'))}\n"
        f"Ubicación reportada: "
        f"{_format_unknown(record.get('reported_location'))}\n"
    )

    if subject_type == "animal":
        base += (
            f"Especie: "
            f"{_animal_species_label(record.get('animal_species'))}\n"
            f"Tamaño: "
            f"{_animal_size_label(record.get('animal_size'))}\n"
            f"Raza / tipo: "
            f"{_format_unknown(record.get('animal_breed'))}\n"
        )
    else:
        base += (
            f"Edad estimada: "
            f"{_format_unknown(record.get('estimated_age'))}\n"
        )

    base += (
        f"Características: "
        f"{_format_unknown(record.get('recognition_features'))}\n"
    )

    if _should_show_public_contact(candidate, record):
        base += (
            f"📞 Medio de contacto: "
            f"{_format_unknown(record.get('public_contact'))}\n"
        )
    elif record.get("public_contact"):
        base += (
            "📞 Medio de contacto: protegido por baja correlación\n"
        )

    base += (
        f"ID HCP: {_format_unknown(record.get('id'))}\n\n"
    )

    return base


def _build_results_keyboard(
    candidates: list[dict],
) -> InlineKeyboardMarkup:
    """
    Builds buttons for candidate explanations and navigation.
    """

    keyboard = []

    for index, candidate in enumerate(candidates, start=1):
        candidate_id = _candidate_callback_id(candidate)

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"ℹ️ ¿Por qué este resultado? #{index}",
                    callback_data=f"explain_{candidate_id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                "🔍 Nueva búsqueda",
                callback_data="search_menu",
            )
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                "⬅️ Volver al menú principal",
                callback_data="back_to_start",
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def _build_empty_keyboard() -> InlineKeyboardMarkup:
    """
    Builds navigation buttons when no candidates are found.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔍 Nueva búsqueda",
                    callback_data="search_menu",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Volver al menú principal",
                    callback_data="back_to_start",
                )
            ],
        ]
    )


async def show_search_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Shows possible related cases using real local HCP records.

    During development, records are loaded from data/hcp_records.json.

    In production, the local storage call can be replaced by an HCP Node
    search endpoint without changing the Telegram conversation flow.
    """

    if not update.message:
        return

    search_data = context.user_data.get(
        "search_record",
        {},
    )
    records = load_records()

    candidates = correlate_records(
        search_data=search_data,
        records=records,
        limit=3,
        min_probability=20,
    )

    _store_candidate_explanations(
        context,
        candidates,
    )

    message = (
        "🔍 Posibles casos relacionados\n\n"
        "HCP no confirma identidades.\n"
        "Relaciona observaciones que podrían corresponder a un mismo caso.\n\n"
        "Datos consultados:\n"
        f"{_format_search_summary(search_data)}"
    )

    if not candidates:
        await update.message.reply_text(
            text=(
                message
                + "No se encontraron posibles casos relacionados con la "
                "información proporcionada.\n\n"
                "Puedes intentar nuevamente modificando datos como:\n\n"
                "• nombre\n"
                "• ubicación\n"
                "• edad aproximada\n"
                "• características para identificación\n\n"
                "Las correlaciones mejoran cuando existen más observaciones "
                "compatibles."
            ),
            reply_markup=_build_empty_keyboard(),
        )
        return

    strong_candidates = [
        candidate
        for candidate in candidates
        if int(candidate.get("probability", 0)) >= 60
    ]

    if strong_candidates:
        message += (
            "Se encontraron posibles casos relacionados.\n\n"
            "📞 Los medios de contacto solo se muestran cuando el reporte "
            f"alcanza al menos {CONTACT_VISIBILITY_THRESHOLD}% de "
            "compatibilidad.\n\n"
            "El contacto nunca participa en el cálculo de correlación.\n\n"
        )
    else:
        message += (
            "No se encontraron coincidencias fuertes.\n\n"
            "Sin embargo, existen observaciones con características "
            "parcialmente similares. Pueden ser útiles para verificación, "
            "pero no deben interpretarse como coincidencias probables.\n\n"
            "📞 Los medios de contacto permanecen protegidos porque ninguna "
            f"observación alcanzó el {CONTACT_VISIBILITY_THRESHOLD}% de "
            "compatibilidad.\n\n"
        )

    for index, candidate in enumerate(candidates, start=1):
        message += _format_candidate(
            index,
            candidate,
        )

    await update.message.reply_text(
        text=message,
        reply_markup=_build_results_keyboard(candidates),
    )

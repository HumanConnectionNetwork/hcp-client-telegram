import asyncio
import logging
from typing import Any

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.hcp.case_presenter import build_case_message
from app.hcp.client import HCPClient
from app.hcp.query_builder import build_hcp_query
from app.search.correlation import correlate_records
from app.storage.hcp_storage import load_records


logger = logging.getLogger(__name__)


CONTACT_VISIBILITY_THRESHOLD = 60
TELEGRAM_MESSAGE_LIMIT = 3900


EVENT_TYPE_LABELS = {
    # HCP 0.5 canonical event types.
    "missing_report": "🚨 Persona desaparecida",
    "hospitalized_report": "🏥 Persona hospitalizada",
    "sheltered_report": "🏠 Persona refugiada",
    "safe_report": "✅ Persona localizada",
    "public_emergency_report": "🆘 Emergencia pública",
    "missing_animal_report": "🐾 Animal desaparecido",
    "found_animal_report": "✅ Animal encontrado",

    # Compatibility with earlier locally stored records.
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
    Return a human-readable value for missing or empty data.
    """

    if value is None:
        return "No especificado"

    text = str(value).strip()

    if not text or text == "0":
        return "No especificado"

    return text


def _event_type_label(value: object) -> str:
    """
    Convert an HCP event type into a Spanish user-facing label.
    """

    key = str(value or "").strip()

    return EVENT_TYPE_LABELS.get(
        key,
        key.replace("_", " ").capitalize()
        if key
        else "No especificado",
    )


def _source_label(value: object) -> str:
    """
    Convert a canonical source value into a Spanish label.
    """

    key = str(value or "").strip()

    return SOURCE_LABELS.get(
        key,
        _format_unknown(value),
    )


def _animal_species_label(value: object) -> str:
    """
    Convert an animal species value into Spanish.
    """

    key = str(value or "").strip()

    return ANIMAL_SPECIES_LABELS.get(
        key,
        _format_unknown(value),
    )


def _animal_size_label(value: object) -> str:
    """
    Convert an animal size value into Spanish.
    """

    key = str(value or "").strip()

    return ANIMAL_SIZE_LABELS.get(
        key,
        _format_unknown(value),
    )


def _candidate_callback_id(candidate: dict[str, Any]) -> str:
    """
    Return a callback identifier that fits Telegram callback_data limits.
    """

    candidate_id = str(
        candidate.get("candidate_id", "unknown")
    )

    return candidate_id[:60]


def _store_candidate_explanations(
    context: ContextTypes.DEFAULT_TYPE,
    candidates: list[dict[str, Any]],
) -> None:
    """
    Store local correlation explanations temporarily for explain.py.
    """

    explanations: dict[str, dict[str, Any]] = {}

    for candidate in candidates:
        candidate_id = _candidate_callback_id(candidate)

        explanations[candidate_id] = {
            "probability": candidate.get("probability", 0),
            "matches": candidate.get("matches", []),
            "warnings": candidate.get("warnings", []),
            "record": candidate.get("record", {}),
        }

    context.user_data["search_explanations"] = explanations


def _clear_candidate_explanations(
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Remove explanations left by an earlier local search.
    """

    context.user_data.pop(
        "search_explanations",
        None,
    )


def _format_search_summary(
    search_data: dict[str, Any],
) -> str:
    """
    Format the information entered by the user during the search.
    """

    category = search_data.get(
        "category",
        "person",
    )

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
            f"{_format_unknown(search_data.get('recognition_features'))}\n"
        )

    return (
        f"👤 Nombre: "
        f"{_format_unknown(search_data.get('reported_name'))}\n"
        f"🎂 Edad aproximada: "
        f"{_format_unknown(search_data.get('estimated_age'))}\n"
        f"📍 Ubicación: "
        f"{_format_unknown(search_data.get('location'))}\n"
        f"🧩 Características: "
        f"{_format_unknown(search_data.get('recognition_features'))}\n"
    )


def _should_show_public_contact(
    candidate: dict[str, Any],
    record: dict[str, Any],
) -> bool:
    """
    Determine whether a locally correlated public contact may be displayed.
    """

    try:
        probability = float(
            candidate.get("probability", 0)
        )
    except (TypeError, ValueError):
        probability = 0.0

    public_contact = str(
        record.get("public_contact") or ""
    ).strip()

    return (
        probability >= CONTACT_VISIBILITY_THRESHOLD
        and bool(public_contact)
    )


def _format_candidate(
    index: int,
    candidate: dict[str, Any],
) -> str:
    """
    Format one locally calculated correlation candidate.
    """

    record = candidate.get(
        "record",
        {},
    )

    if not isinstance(record, dict):
        record = {}

    subject_type = record.get(
        "subject_type",
        "human",
    )

    try:
        probability = int(
            float(candidate.get("probability", 0))
        )
    except (TypeError, ValueError):
        probability = 0

    message = (
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
        message += (
            f"Especie: "
            f"{_animal_species_label(record.get('animal_species'))}\n"
            f"Tamaño: "
            f"{_animal_size_label(record.get('animal_size'))}\n"
            f"Raza / tipo: "
            f"{_format_unknown(record.get('animal_breed'))}\n"
        )
    else:
        message += (
            f"Edad estimada: "
            f"{_format_unknown(record.get('estimated_age'))}\n"
        )

    message += (
        f"Características: "
        f"{_format_unknown(record.get('recognition_features'))}\n"
    )

    if _should_show_public_contact(
        candidate,
        record,
    ):
        message += (
            f"📞 Medio de contacto: "
            f"{_format_unknown(record.get('public_contact'))}\n"
        )
    elif record.get("public_contact"):
        message += (
            "📞 Medio de contacto: protegido por baja correlación\n"
        )

    message += (
        f"ID HCP: {_format_unknown(record.get('id'))}\n\n"
    )

    return message


def _build_remote_results_keyboard() -> InlineKeyboardMarkup:
    """
    Build navigation buttons for a result returned by an HCP Node.
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


def _build_local_results_keyboard(
    candidates: list[dict[str, Any]],
) -> InlineKeyboardMarkup:
    """
    Build explanation and navigation buttons for local fallback results.
    """

    keyboard: list[list[InlineKeyboardButton]] = []

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        candidate_id = _candidate_callback_id(
            candidate
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"ℹ️ ¿Por qué este resultado? #{index}",
                    callback_data=f"explain_{candidate_id}",
                )
            ]
        )

    keyboard.extend(
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

    return InlineKeyboardMarkup(
        keyboard
    )


def _build_empty_keyboard() -> InlineKeyboardMarkup:
    """
    Build navigation buttons when no result is available.
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


def _split_message(
    text: str,
    limit: int = TELEGRAM_MESSAGE_LIMIT,
) -> list[str]:
    """
    Split a long message into Telegram-safe chunks.

    Paragraph boundaries are preferred so sections remain readable.
    """

    if len(text) <= limit:
        return [text]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = (
            f"{current}\n\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        while len(paragraph) > limit:
            split_at = paragraph.rfind(
                "\n",
                0,
                limit,
            )

            if split_at <= 0:
                split_at = limit

            chunks.append(
                paragraph[:split_at].strip()
            )
            paragraph = paragraph[split_at:].strip()

        current = paragraph

    if current:
        chunks.append(current)

    return chunks


async def _send_message(
    update: Update,
    text: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    """
    Send one or more Telegram messages and attach buttons to the final chunk.
    """

    if not update.message:
        return

    chunks = _split_message(
        text
    )

    for index, chunk in enumerate(chunks):
        is_last = index == len(chunks) - 1

        await update.message.reply_text(
            text=chunk,
            reply_markup=(
                reply_markup
                if is_last
                else None
            ),
        )


async def _search_remote_node(
    search_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a canonical query and send it to the configured HCP Node.

    The synchronous requests client runs in a worker thread so the Telegram
    event loop is not blocked.
    """

    query = build_hcp_query(
        search_data
    )
    client = HCPClient()

    response = await asyncio.to_thread(
        client.search_records,
        query,
    )

    if not isinstance(response, dict):
        raise TypeError(
            "The HCP Node search response must be a dictionary"
        )

    return response


async def _show_local_fallback_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    search_data: dict[str, Any],
) -> None:
    """
    Search locally stored records when the configured HCP Node is unavailable.
    """

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
        "⚠️ El nodo HCP no está disponible en este momento.\n\n"
        "La búsqueda fue realizada usando las observaciones guardadas "
        "localmente en este cliente.\n\n"
        "🔍 Posibles casos relacionados\n\n"
        "HCP no confirma identidades.\n"
        "Relaciona observaciones que podrían corresponder a un mismo caso.\n\n"
        "Datos consultados:\n"
        f"{_format_search_summary(search_data)}\n"
    )

    if not candidates:
        message += (
            "\nNo se encontraron posibles casos relacionados con la "
            "información proporcionada.\n\n"
            "Puedes intentar nuevamente modificando datos como:\n\n"
            "• nombre\n"
            "• ubicación\n"
            "• edad aproximada\n"
            "• características para identificación\n\n"
            "Las correlaciones mejoran cuando existen más observaciones "
            "compatibles."
        )

        await _send_message(
            update=update,
            text=message,
            reply_markup=_build_empty_keyboard(),
        )
        return

    strong_candidates = [
        candidate
        for candidate in candidates
        if float(candidate.get("probability", 0)) >= 60
    ]

    if strong_candidates:
        message += (
            "\nSe encontraron posibles casos relacionados.\n\n"
            "📞 Los medios de contacto solo se muestran cuando el reporte "
            f"alcanza al menos {CONTACT_VISIBILITY_THRESHOLD}% de "
            "compatibilidad.\n\n"
            "El contacto nunca participa en el cálculo de correlación.\n\n"
        )
    else:
        message += (
            "\nNo se encontraron coincidencias fuertes.\n\n"
            "Sin embargo, existen observaciones con características "
            "parcialmente similares. Pueden ser útiles para verificación, "
            "pero no deben interpretarse como coincidencias probables.\n\n"
            "📞 Los medios de contacto permanecen protegidos porque ninguna "
            f"observación alcanzó el {CONTACT_VISIBILITY_THRESHOLD}% de "
            "compatibilidad.\n\n"
        )

    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        message += _format_candidate(
            index,
            candidate,
        )

    await _send_message(
        update=update,
        text=message,
        reply_markup=_build_local_results_keyboard(
            candidates
        ),
    )


async def show_search_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Search an HCP Node and present the resulting Humanitarian Case.

    Normal flow:

        search data
            -> HumanitarianQuery
            -> POST /hcp/search
            -> SearchResponse
            -> HumanitarianCase presentation

    If the HCP Node cannot be reached, the existing local storage and
    correlation implementation are used as an offline fallback.
    """

    if not update.message:
        return

    search_data = context.user_data.get(
        "search_record",
        {},
    )

    if not isinstance(search_data, dict):
        search_data = {}

    try:
        search_response = await _search_remote_node(
            search_data
        )

        _clear_candidate_explanations(
            context
        )

        message = build_case_message(
            search_response
        )

        await _send_message(
            update=update,
            text=message,
            reply_markup=_build_remote_results_keyboard(),
        )

    except (
        requests.RequestException,
        TimeoutError,
        ConnectionError,
    ) as exc:
        logger.warning(
            "HCP Node search failed; using local fallback: %s",
            exc,
        )

        await _show_local_fallback_results(
            update=update,
            context=context,
            search_data=search_data,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        logger.exception(
            "Invalid HCP query or search response: %s",
            exc,
        )

        await update.message.reply_text(
            text=(
                "⚠️ No fue posible procesar esta búsqueda.\n\n"
                "Algunos datos no pudieron convertirse correctamente al "
                "formato HCP. Regresa al menú e intenta realizar una nueva "
                "búsqueda."
            ),
            reply_markup=_build_empty_keyboard(),
        )

    except Exception as exc:
        logger.exception(
            "Unexpected error while searching HCP records: %s",
            exc,
        )

        await update.message.reply_text(
            text=(
                "⚠️ Ocurrió un error inesperado durante la búsqueda.\n\n"
                "Puedes intentar nuevamente o regresar al menú principal."
            ),
            reply_markup=_build_empty_keyboard(),
        )

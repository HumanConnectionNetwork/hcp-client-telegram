from __future__ import annotations

from datetime import datetime
from typing import Any


MAX_SUPPORTING_SIGNALS = 3
MAX_CONFLICTING_SIGNALS = 3


EVENT_TYPE_LABELS = {
    "missing": "Persona desaparecida",
    "missing_report": "Persona desaparecida",
    "missing_person": "Persona desaparecida",
    "hospitalized": "Persona hospitalizada",
    "hospitalized_report": "Persona hospitalizada",
    "hospitalized_person": "Persona hospitalizada",
    "sheltered": "Persona refugiada",
    "sheltered_report": "Persona refugiada",
    "refugee": "Persona refugiada",
    "safe": "Persona localizada o a salvo",
    "safe_report": "Persona localizada o a salvo",
    "found": "Persona localizada",
    "found_person": "Persona localizada",
    "public_emergency": "Emergencia pública",
    "public_emergency_report": "Emergencia pública",
    "missing_animal": "Animal desaparecido",
    "missing_animal_report": "Animal desaparecido",
    "found_animal": "Animal encontrado",
    "found_animal_report": "Animal encontrado",
}


EVIDENCE_LEVEL_LABELS = {
    "very_low": "Muy bajo",
    "low": "Bajo",
    "medium": "Medio",
    "moderate": "Medio",
    "high": "Alto",
    "very_high": "Muy alto",
}


VERIFICATION_STATUS_LABELS = {
    "unverified": "⚪ No verificado",
    "pending": "🟡 Pendiente de verificación",
    "partially_verified": "🟠 Verificación parcial",
    "verified": "🟢 Verificado",
    "rejected": "🔴 Rechazado",
}


SOURCE_LABELS = {
    "family": "Familia",
    "hospital": "Hospital",
    "fire_department": "Bomberos",
    "volunteer": "Voluntario",
    "police": "Policía",
    "friend": "Amigo o conocido",
    "unknown": "Fuente no especificada",
    "swagger_manual_test": "Prueba manual del nodo",
}


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    return []


def _first_value(
    data: dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    for key in keys:
        value = data.get(key)

        if value not in (None, "", [], {}):
            return value

    return default


def _nested_value(
    data: dict[str, Any],
    *paths: tuple[str, ...],
    default: Any = None,
) -> Any:
    for path in paths:
        current: Any = data

        for key in path:
            if not isinstance(current, dict):
                current = None
                break

            current = current.get(key)

        if current not in (None, "", [], {}):
            return current

    return default


def _clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _normalize_key(value: Any) -> str:
    return (
        _clean_text(value)
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _format_event_type(value: Any) -> str:
    key = _normalize_key(value)

    if not key:
        return "No especificado"

    return EVENT_TYPE_LABELS.get(
        key,
        key.replace("_", " ").capitalize(),
    )


def _format_evidence_level(value: Any) -> str:
    key = _normalize_key(value)

    if not key:
        return "No especificado"

    return EVIDENCE_LEVEL_LABELS.get(
        key,
        key.replace("_", " ").capitalize(),
    )


def _format_verification_status(value: Any) -> str:
    key = _normalize_key(value)

    if not key:
        return "⚪ No verificado"

    return VERIFICATION_STATUS_LABELS.get(
        key,
        key.replace("_", " ").capitalize(),
    )


def _format_source(value: Any) -> str:
    key = _normalize_key(value)

    if not key:
        return "Fuente no especificada"

    return SOURCE_LABELS.get(
        key,
        key.replace("_", " ").capitalize(),
    )


def _format_percentage(value: Any) -> str:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return "No disponible"

    if 0 <= score <= 1:
        score *= 100

    return f"{score:.0f}%"


def _format_datetime(value: Any) -> str:
    text = _clean_text(value)

    if not text:
        return "No especificada"

    try:
        normalized = text.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)

        return parsed.strftime("%d/%m/%Y, %H:%M UTC")
    except ValueError:
        return text


def _translate_signal_title(value: Any) -> str:
    text = _clean_text(value)
    key = _normalize_key(text)

    translations = {
        "subject_reported_label_match": (
            "El nombre reportado coincide"
        ),
        "subject_reported_label_partial_match": (
            "El nombre presenta similitud parcial"
        ),
        "subject_reported_label_conflict": (
            "El nombre reportado presenta diferencias"
        ),
        "subject_estimated_age_match": (
            "La edad estimada coincide"
        ),
        "subject_estimated_age_partial_match": (
            "La edad estimada es similar"
        ),
        "subject_estimated_age_conflict": (
            "La edad estimada no coincide"
        ),
        "subject_recognition_features_match": (
            "Las características para identificación coinciden"
        ),
        "subject_recognition_features_partial_match": (
            "Las características presentan similitud parcial"
        ),
        "subject_recognition_features_conflict": (
            "Las características tienen poca similitud"
        ),
        "observation_reported_location_match": (
            "La ubicación reportada coincide"
        ),
        "observation_reported_location_partial_match": (
            "La ubicación presenta similitud parcial"
        ),
        "observation_reported_location_conflict": (
            "La ubicación reportada no coincide"
        ),
        "observation_temporal_proximity_match": (
            "Las observaciones son cercanas en el tiempo"
        ),
        "observation_temporal_proximity_conflict": (
            "Las fechas de las observaciones son distantes"
        ),
        "observation_event_type_match": (
            "El tipo de situación coincide"
        ),
        "observation_event_type_conflict": (
            "El tipo de situación presenta diferencias"
        ),
    }

    if key in translations:
        return translations[key]

    if "reported_label" in key:
        if "conflict" in key:
            return "El nombre reportado presenta diferencias"
        if "partial" in key:
            return "El nombre presenta similitud parcial"
        return "El nombre reportado coincide"

    if "estimated_age" in key:
        if "conflict" in key:
            return "La edad estimada no coincide"
        if "partial" in key:
            return "La edad estimada es similar"
        return "La edad estimada coincide"

    if "recognition_features" in key:
        if "conflict" in key:
            return "Las características tienen poca similitud"
        if "partial" in key:
            return "Las características presentan similitud parcial"
        return "Las características para identificación coinciden"

    if "reported_location" in key or "location" in key:
        if "conflict" in key:
            return "La ubicación reportada no coincide"
        if "partial" in key:
            return "La ubicación presenta similitud parcial"
        return "La ubicación reportada coincide"

    if "temporal" in key or "date" in key:
        if "conflict" in key:
            return "Las fechas presentan diferencias"
        return "Las observaciones son cercanas en el tiempo"

    if "event_type" in key:
        if "conflict" in key:
            return "El tipo de situación presenta diferencias"
        return "El tipo de situación coincide"

    return (
        text.replace("_", " ").capitalize()
        if text
        else "Señal de correlación"
    )


def _extract_signal_title(signal: Any) -> str:
    if isinstance(signal, str):
        return _translate_signal_title(signal)

    signal_data = _as_dict(signal)

    raw_title = _first_value(
        signal_data,
        "type",
        "signal_type",
        "code",
        "title",
        "label",
        "name",
        default="",
    )

    return _translate_signal_title(raw_title)


def _extract_case(
    search_response: dict[str, Any],
) -> dict[str, Any]:
    case = search_response.get("humanitarian_case")

    if isinstance(case, dict):
        return case

    case = search_response.get("case")

    if isinstance(case, dict):
        return case

    return search_response


def _extract_interpretation(
    case: dict[str, Any],
) -> dict[str, Any]:
    return _as_dict(
        _first_value(
            case,
            "interpreted_situation",
            "situation",
            "interpretation",
            "current_situation",
            default={},
        )
    )


def _extract_correlation(
    case: dict[str, Any],
) -> dict[str, Any]:
    return _as_dict(
        _first_value(
            case,
            "correlation",
            "correlation_summary",
            "assessment",
            default={},
        )
    )


def _extract_verification(
    case: dict[str, Any],
) -> dict[str, Any]:
    return _as_dict(
        _first_value(
            case,
            "verification",
            "verification_status",
            default={},
        )
    )


def _extract_supporting_signals(
    case: dict[str, Any],
    correlation: dict[str, Any],
) -> list[Any]:
    signals = _first_value(
        correlation,
        "supporting_signals",
        "supporting_evidence",
        "compatible_evidence",
        "matches",
        default=None,
    )

    if signals is None:
        signals = _first_value(
            case,
            "supporting_signals",
            "supporting_evidence",
            "compatible_evidence",
            default=[],
        )

    return _as_list(signals)


def _extract_conflicting_signals(
    case: dict[str, Any],
    correlation: dict[str, Any],
) -> list[Any]:
    signals = _first_value(
        correlation,
        "conflicting_signals",
        "conflicting_evidence",
        "warnings",
        "conflicts",
        default=None,
    )

    if signals is None:
        signals = _first_value(
            case,
            "conflicting_signals",
            "conflicting_evidence",
            "warnings",
            default=[],
        )

    return _as_list(signals)


def _extract_related_records(
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    records = _first_value(
        case,
        "related_records",
        "records",
        "correlated_records",
        "observations",
        default=[],
    )

    return [
        record
        for record in _as_list(records)
        if isinstance(record, dict)
    ]


def _extract_candidate_count(
    search_response: dict[str, Any],
    case: dict[str, Any],
    related_records: list[dict[str, Any]],
) -> int:
    value = _first_value(
        search_response,
        "correlated_count",
        "candidate_count",
        default=None,
    )

    if value is None:
        value = _first_value(
            case,
            "correlated_count",
            "related_record_count",
            "record_count",
            default=len(related_records),
        )

    try:
        return int(value)
    except (TypeError, ValueError):
        return len(related_records)


def _build_signal_section(
    title: str,
    signals: list[Any],
    limit: int,
) -> str:
    if not signals:
        return ""

    lines = [title]

    for signal in signals[:limit]:
        lines.append(
            f"• {_extract_signal_title(signal)}."
        )

    remaining = len(signals) - limit

    if remaining > 0:
        lines.append(
            f"• Hay {remaining} señal(es) adicional(es) "
            "en la interpretación completa."
        )

    return "\n".join(lines)


def _build_related_records_summary(
    records: list[dict[str, Any]],
) -> str:
    if not records:
        return ""

    lines = [
        "📄 Observaciones relacionadas",
    ]

    for index, record in enumerate(
        records[:3],
        start=1,
    ):
        observation = _as_dict(
            record.get("observation")
        )

        event_type = _first_value(
            record,
            "event_type",
            default=None,
        )

        if event_type is None:
            event_type = _first_value(
                observation,
                "event_type",
                "type",
                default="",
            )

        observed_at = _first_value(
            record,
            "observed_at",
            "timestamp",
            "date",
            default=None,
        )

        if observed_at is None:
            observed_at = _first_value(
                observation,
                "observed_at",
                "timestamp",
                default="",
            )

        source = _first_value(
            record,
            "source",
            "reported_by",
            default=None,
        )

        if source is None:
            source = _first_value(
                observation,
                "source",
                "reported_by",
                default="",
            )

        lines.extend(
            [
                "",
                f"#{index} {_format_event_type(event_type)}",
                f"🕒 {_format_datetime(observed_at)}",
                f"🏷️ Fuente: {_format_source(source)}",
            ]
        )

    if len(records) > 3:
        lines.extend(
            [
                "",
                f"Hay {len(records) - 3} observación(es) adicional(es) "
                "relacionada(s).",
            ]
        )

    return "\n".join(lines)


def build_case_message(
    search_response: dict[str, Any],
) -> str:
    """
    Convert an HCP SearchResponse or HumanitarianCase into a concise,
    Spanish-language Telegram message.

    HCP does not confirm identity. The message presents a probabilistic
    interpretation and highlights the main compatible and conflicting signals.
    """

    if not isinstance(search_response, dict):
        raise TypeError(
            "search_response must be a dictionary"
        )

    case = _extract_case(
        search_response
    )

    if not case:
        return (
            "🔍 Resultado de la búsqueda\n\n"
            "No se encontraron observaciones relacionadas con los datos "
            "proporcionados.\n\n"
            "Puedes intentar nuevamente modificando el nombre, la edad, "
            "la ubicación o las características para identificación."
        )

    interpretation = _extract_interpretation(
        case
    )
    correlation = _extract_correlation(
        case
    )
    verification = _extract_verification(
        case
    )
    related_records = _extract_related_records(
        case
    )

    supporting_signals = _extract_supporting_signals(
        case,
        correlation,
    )
    conflicting_signals = _extract_conflicting_signals(
        case,
        correlation,
    )

    event_type = _first_value(
        interpretation,
        "event_type",
        "probable_event_type",
        "type",
        "status",
        default=None,
    )

    if event_type is None:
        event_type = _first_value(
            case,
            "event_type",
            "probable_event_type",
            default="",
        )

    location = _first_value(
        interpretation,
        "reported_location",
        "location",
        default=None,
    )

    if location is None:
        location = _first_value(
            case,
            "reported_location",
            "location",
            default="No especificada",
        )

    observed_at = _first_value(
        interpretation,
        "observed_at",
        "observation_date",
        "timestamp",
        default=None,
    )

    if observed_at is None:
        observed_at = _first_value(
            case,
            "observed_at",
            "generated_at",
            default="",
        )

    score = _first_value(
        correlation,
        "score",
        "correlation_score",
        "compatibility",
        "probability",
        default=None,
    )

    if score is None:
        score = _first_value(
            case,
            "correlation_score",
            "compatibility",
            "probability",
            default=None,
        )

    evidence_level = _first_value(
        correlation,
        "evidence_level",
        "level",
        default=None,
    )

    if evidence_level is None:
        evidence_level = _first_value(
            case,
            "evidence_level",
            default="",
        )

    verification_status = _first_value(
        verification,
        "status",
        "state",
        default=None,
    )

    if verification_status is None:
        verification_status = _first_value(
            case,
            "verification_status",
            default="unverified",
        )

    record_count = _extract_candidate_count(
        search_response,
        case,
        related_records,
    )

    if record_count <= 0:
        return (
            "🔍 Resultado de la búsqueda\n\n"
            "No se encontraron observaciones suficientemente relacionadas "
            "con los datos proporcionados.\n\n"
            "Puedes intentar nuevamente modificando el nombre, la edad, "
            "la ubicación o las características para identificación."
        )

    message_parts = [
        "🔍 Posible caso relacionado",
        (
            "HCP no confirma identidades.\n"
            "Relaciona observaciones que podrían corresponder "
            "a un mismo caso."
        ),
        (
            f"📊 Compatibilidad: {_format_percentage(score)}\n"
            f"🧭 Nivel de evidencia: "
            f"{_format_evidence_level(evidence_level)}"
        ),
        (
            f"📍 Estado probable: {_format_event_type(event_type)}\n"
            f"📌 Ubicación: {_clean_text(location) or 'No especificada'}\n"
            f"🕒 Observación más relevante: "
            f"{_format_datetime(observed_at)}"
        ),
        (
            f"Se encontraron {record_count} "
            f"observación(es) relacionada(s)."
        ),
    ]

    supporting_section = _build_signal_section(
        "✅ Coincidencias principales",
        supporting_signals,
        MAX_SUPPORTING_SIGNALS,
    )

    if supporting_section:
        message_parts.append(
            supporting_section
        )

    conflicting_section = _build_signal_section(
        "⚠️ Diferencias importantes",
        conflicting_signals,
        MAX_CONFLICTING_SIGNALS,
    )

    if conflicting_section:
        message_parts.append(
            conflicting_section
        )

    related_records_section = _build_related_records_summary(
        related_records
    )

    if related_records_section:
        message_parts.append(
            related_records_section
        )

    message_parts.append(
        (
            "🛡️ Verificación\n"
            f"Estado: "
            f"{_format_verification_status(verification_status)}\n\n"
            "Este resultado necesita verificación humana. "
            "Revisa las observaciones y sus fuentes antes de tomar "
            "una decisión."
        )
    )

    return "\n\n──────────────\n\n".join(
        message_parts
    )

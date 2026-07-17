from typing import Any


CONTACT_VISIBILITY_THRESHOLD = 60.0


EVENT_TYPE_LABELS = {
    "missing_report": "🚨 Persona desaparecida",
    "hospitalized_report": "🏥 Persona hospitalizada",
    "sheltered_report": "🏠 Persona refugiada",
    "safe_report": "✅ Persona localizada",
    "public_emergency_report": "🆘 Emergencia pública",
    "missing_animal_report": "🐾 Animal desaparecido",
    "found_animal_report": "✅ Animal encontrado",
    # Compatibility with earlier values.
    "missing_person": "🚨 Persona desaparecida",
    "hospitalized_person": "🏥 Persona hospitalizada",
    "sheltered_person": "🏠 Persona refugiada",
    "safe_person": "✅ Persona localizada",
    "missing_animal": "🐾 Animal desaparecido",
    "found_animal": "✅ Animal encontrado",
}


VERIFICATION_LABELS = {
    "unverified": "⚪ No verificado",
    "under_review": "🟡 En revisión",
    "human_verified": "🟢 Verificado por una persona",
    "rejected": "🔴 Rechazado",
}


EVIDENCE_LEVEL_LABELS = {
    "very_low": "Muy baja",
    "low": "Baja",
    "medium": "Media",
    "high": "Alta",
    "very_high": "Muy alta",
}


def _clean_text(value: Any) -> str | None:
    """
    Return normalized non-empty text.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def _display_value(
    value: Any,
    default: str = "No especificado",
) -> str:
    """
    Convert an optional value into user-facing text.
    """

    text = _clean_text(value)

    if text is None:
        return default

    return text


def _format_score(value: Any) -> str:
    """
    Format a correlation score without unnecessary decimal places.
    """

    try:
        score = float(value)
    except (TypeError, ValueError):
        return "No especificada"

    if score.is_integer():
        return f"{int(score)}%"

    return f"{score:.1f}%"


def _event_type_label(value: Any) -> str:
    """
    Convert an HCP event type into a Spanish user-facing label.
    """

    event_type = _clean_text(value)

    if event_type is None:
        return "No especificado"

    return EVENT_TYPE_LABELS.get(
        event_type,
        event_type.replace("_", " ").capitalize(),
    )


def _verification_label(value: Any) -> str:
    """
    Convert a verification status into a Spanish label.
    """

    status = _clean_text(value)

    if status is None:
        return "No especificado"

    return VERIFICATION_LABELS.get(
        status,
        status.replace("_", " ").capitalize(),
    )


def _evidence_level_label(value: Any) -> str:
    """
    Convert a correlation evidence level into a readable label.
    """

    level = _clean_text(value)

    if level is None:
        return "No especificado"

    return EVIDENCE_LEVEL_LABELS.get(
        level,
        level.replace("_", " ").capitalize(),
    )


def _format_timestamp(value: Any) -> str:
    """
    Format a canonical timestamp for Telegram.

    The canonical ISO 8601 value is preserved to avoid timezone ambiguity.
    """

    return _display_value(value)


def _format_current_situation(
    current_situation: dict[str, Any] | None,
) -> str:
    """
    Format the optional current local interpretation.
    """

    if not isinstance(current_situation, dict):
        return ""

    lines = [
        "📍 Situación interpretada actualmente",
    ]

    likely_event_type = current_situation.get(
        "likely_event_type"
    )
    reported_location = current_situation.get(
        "reported_location"
    )
    observed_at = current_situation.get(
        "observed_at"
    )

    if likely_event_type is not None:
        lines.append(
            f"Tipo probable: {_event_type_label(likely_event_type)}"
        )

    if reported_location is not None:
        lines.append(
            f"Ubicación reportada: "
            f"{_display_value(reported_location)}"
        )

    if observed_at is not None:
        lines.append(
            f"Fecha de observación: "
            f"{_format_timestamp(observed_at)}"
        )

    if len(lines) == 1:
        return ""

    return "\n".join(lines)


def _format_evidence_items(
    title: str,
    items: Any,
) -> str:
    """
    Format supporting or conflicting evidence items.
    """

    if not isinstance(items, list) or not items:
        return ""

    lines = [title]

    for item in items:
        if not isinstance(item, dict):
            continue

        description = _display_value(
            item.get("description")
        )
        evidence_type = _clean_text(
            item.get("type")
        )
        related_ids = item.get(
            "related_record_ids",
            [],
        )

        prefix = "•"

        if evidence_type:
            readable_type = evidence_type.replace(
                "_",
                " ",
            ).capitalize()
            lines.append(
                f"{prefix} {readable_type}: {description}"
            )
        else:
            lines.append(
                f"{prefix} {description}"
            )

        if isinstance(related_ids, list) and related_ids:
            record_ids = ", ".join(
                str(record_id)
                for record_id in related_ids
            )
            lines.append(
                f"  Registros relacionados: {record_ids}"
            )

    if len(lines) == 1:
        return ""

    return "\n".join(lines)


def _format_correlation(
    correlation: dict[str, Any] | None,
) -> str:
    """
    Format the node's local correlation interpretation.
    """

    if not isinstance(correlation, dict):
        return (
            "📊 Correlación\n"
            "No se recibió información de correlación."
        )

    lines = [
        "📊 Correlación",
        f"Compatibilidad: "
        f"{_format_score(correlation.get('score'))}",
        f"Nivel de evidencia: "
        f"{_evidence_level_label(correlation.get('evidence_level'))}",
    ]

    reasoning = _clean_text(
        correlation.get("reasoning")
    )

    if reasoning:
        lines.extend(
            [
                "",
                "Explicación:",
                reasoning,
            ]
        )

    supporting = _format_evidence_items(
        "✅ Evidencia compatible",
        correlation.get("supporting_evidence"),
    )

    if supporting:
        lines.extend(
            [
                "",
                supporting,
            ]
        )

    conflicting = _format_evidence_items(
        "⚠️ Evidencia incompatible o dudosa",
        correlation.get("conflicting_evidence"),
    )

    if conflicting:
        lines.extend(
            [
                "",
                conflicting,
            ]
        )

    return "\n".join(lines)


def _format_related_records(
    related_records: Any,
) -> str:
    """
    Format immutable Humanitarian Record references.
    """

    if not isinstance(related_records, list) or not related_records:
        return ""

    lines = [
        "📄 Observaciones relacionadas",
    ]

    for index, record in enumerate(
        related_records,
        start=1,
    ):
        if not isinstance(record, dict):
            continue

        record_id = _display_value(
            record.get("record_id")
        )
        event_type = _event_type_label(
            record.get("event_type")
        )
        observed_at = _format_timestamp(
            record.get("observed_at")
        )
        source = _clean_text(
            record.get("source")
        )

        lines.extend(
            [
                "",
                f"#{index} {event_type}",
                f"ID: {record_id}",
                f"Fecha: {observed_at}",
            ]
        )

        if source:
            lines.append(
                f"Fuente: {source}"
            )

    if len(lines) == 1:
        return ""

    return "\n".join(lines)


def _format_timeline(
    timeline: Any,
) -> str:
    """
    Format the local chronological presentation of observations.
    """

    if not isinstance(timeline, list) or not timeline:
        return ""

    lines = [
        "🕒 Línea de observaciones",
    ]

    for entry in timeline:
        if not isinstance(entry, dict):
            continue

        event_type = _event_type_label(
            entry.get("event_type")
        )
        observed_at = _format_timestamp(
            entry.get("observed_at")
        )
        location = _clean_text(
            entry.get("reported_location")
        )
        description = _clean_text(
            entry.get("description")
        )
        record_id = _display_value(
            entry.get("record_id")
        )

        lines.extend(
            [
                "",
                f"• {event_type}",
                f"  Fecha: {observed_at}",
            ]
        )

        if location:
            lines.append(
                f"  Ubicación: {location}"
            )

        if description:
            lines.append(
                f"  Detalle: {description}"
            )

        lines.append(
            f"  ID: {record_id}"
        )

    if len(lines) == 1:
        return ""

    return "\n".join(lines)


def _format_verification(
    verification: dict[str, Any] | None,
) -> str:
    """
    Format the local verification state of the Humanitarian Case.
    """

    if not isinstance(verification, dict):
        return (
            "🛡️ Verificación\n"
            "Estado: No especificado"
        )

    lines = [
        "🛡️ Verificación",
        f"Estado: "
        f"{_verification_label(verification.get('status'))}",
    ]

    message = _clean_text(
        verification.get("message")
    )
    verified_by = _clean_text(
        verification.get("verified_by")
    )
    verified_at = _clean_text(
        verification.get("verified_at")
    )

    if message:
        lines.append(
            f"Información: {message}"
        )

    if verified_by:
        lines.append(
            f"Verificado por: {verified_by}"
        )

    if verified_at:
        lines.append(
            f"Fecha de verificación: {verified_at}"
        )

    return "\n".join(lines)


def build_empty_search_message(
    search_response: dict[str, Any] | None = None,
) -> str:
    """
    Build the Telegram message used when no Humanitarian Case was generated.
    """

    candidate_count = 0
    correlated_count = 0

    if isinstance(search_response, dict):
        candidate_count = search_response.get(
            "candidate_count",
            0,
        )
        correlated_count = search_response.get(
            "correlated_count",
            0,
        )

    return (
        "🔍 No se encontraron casos suficientemente relacionados.\n\n"
        "HCP puede haber encontrado observaciones generales, pero ninguna "
        "alcanzó el nivel de compatibilidad necesario para construir un "
        "caso humanitario local.\n\n"
        f"Observaciones evaluadas inicialmente: {candidate_count}\n"
        f"Observaciones correlacionadas: {correlated_count}\n\n"
        "Puedes intentar nuevamente usando otra ubicación, una edad "
        "aproximada diferente o características más específicas.\n\n"
        "HCP no confirma identidades. Relaciona observaciones que podrían "
        "corresponder a un mismo caso."
    )


def build_case_message(
    search_response: dict[str, Any],
) -> str:
    """
    Convert an HCP SearchResponse into a Telegram-friendly message.

    The function presents the Humanitarian Case exactly as a local,
    probabilistic interpretation. It must never describe the result as a
    confirmed identity.

    Args:
        search_response:
            JSON response returned by POST /hcp/search.

    Returns:
        A complete Telegram message.

    Raises:
        TypeError:
            If search_response is not a dictionary.
    """

    if not isinstance(search_response, dict):
        raise TypeError(
            "search_response must be a dictionary"
        )

    humanitarian_case = search_response.get(
        "humanitarian_case"
    )

    if not isinstance(humanitarian_case, dict):
        return build_empty_search_message(
            search_response
        )

    candidate_count = search_response.get(
        "candidate_count",
        0,
    )
    correlated_count = search_response.get(
        "correlated_count",
        0,
    )

    case_id = _display_value(
        humanitarian_case.get("case_id")
    )
    generated_at = _format_timestamp(
        humanitarian_case.get("generated_at")
    )
    summary = _display_value(
        humanitarian_case.get("humanitarian_summary")
    )

    sections = [
        "🔍 Posible caso humanitario relacionado",
        "",
        "HCP no confirma identidades.",
        "Este resultado es una interpretación probabilística construida a "
        "partir de observaciones compatibles.",
        "",
        f"Resumen:\n{summary}",
        "",
        f"Observaciones evaluadas inicialmente: {candidate_count}",
        f"Observaciones relacionadas: {correlated_count}",
        f"ID local del caso: {case_id}",
        f"Generado: {generated_at}",
    ]

    optional_sections = [
        _format_current_situation(
            humanitarian_case.get("current_situation")
        ),
        _format_correlation(
            humanitarian_case.get("correlation")
        ),
        _format_related_records(
            humanitarian_case.get("related_records")
        ),
        _format_timeline(
            humanitarian_case.get("humanitarian_timeline")
        ),
        _format_verification(
            humanitarian_case.get("verification")
        ),
    ]

    for section in optional_sections:
        if section:
            sections.extend(
                [
                    "",
                    "──────────────",
                    "",
                    section,
                ]
            )

    sections.extend(
        [
            "",
            "⚠️ Revisa las observaciones y sus fuentes antes de tomar una "
            "decisión. Un caso humanitario no sustituye la verificación "
            "humana.",
        ]
    )

    return "\n".join(sections)

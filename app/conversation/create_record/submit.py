from telegram import Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.models.humanitarian_record import HumanitarianRecord


async def submit_record(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    record = HumanitarianRecord(
        reported_name=context.user_data.get("reported_name", "Desconocido"),
        estimated_age=context.user_data.get("estimated_age", "Desconocido"),
        reported_location=context.user_data.get("reported_location", "Desconocido"),
        event_type=context.user_data.get("event_type", "unknown"),
        status="reported",
        source=context.user_data.get("source", "unknown"),
        description=context.user_data.get("description", ""),
    )

    payload = record.to_json()

    print("HCP Record payload:")
    print(payload)

    context.user_data["record_step"] = states.SUBMIT

    await query.edit_message_text(
        text=(
            "✅ Reporte preparado correctamente.\n\n"
            "Gracias por contribuir.\n\n"
            "Tu reporte ha sido registrado como una observación humanitaria.\n\n"
            "HCP no busca identificar personas.\n"
            "HCP relaciona observaciones humanitarias para facilitar búsquedas, "
            "verificación y posibles coincidencias durante una emergencia.\n\n"
            "📄 Registro HCP\n\n"
            f"ID:\n{record.record_id}\n\n"
            f"Fecha:\n{record.created_at}\n\n"
            "Estado:\n🟢 Preparado correctamente\n\n"
            "Puedes compartir este identificador con familiares, organizaciones "
            "o equipos de búsqueda cuando necesites hacer referencia a este reporte."
        )
    )

    context.user_data.clear()

from telegram import Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.hcp.record_builder import build_hcp_record
from app.storage.hcp_storage import add_record


async def submit_record(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Final confirmation step.

    Builds a canonical HCP record and stores it locally.
    Later this storage layer will be replaced by the HCP Node API.
    """

    query = update.callback_query

    if not query:
        return

    await query.answer()

    # ---------------------------------------------------------
    # Build canonical HCP record
    # ---------------------------------------------------------

    record = build_hcp_record(context.user_data)

    # ---------------------------------------------------------
    # Local persistence (development only)
    # ---------------------------------------------------------

    add_record(record)

    print("\n==============================")
    print("New HCP Record")
    print("==============================")
    print(record)
    print("==============================\n")

    context.user_data["record_step"] = states.SUBMIT

    # ---------------------------------------------------------
    # Confirmation message
    # ---------------------------------------------------------

    await query.edit_message_text(
    text="✅ Reporte registrado correctamente."
)

language = context.user_data.get("language")

context.user_data.clear()

if language:
    context.user_data["language"] = language

context.user_data["last_record_id"] = record["id"]

return await start_menu(update, context)

await update.effective_chat.send_message(
    text=(
        "📌 Guarda este ID.\n\n"
        "Con él podrás consultar nuevamente esta observación "
        "y buscar reportes relacionados más recientes."
    )
)

    # ---------------------------------------------------------
    # Clean conversation
    # ---------------------------------------------------------

    context.user_data.clear()

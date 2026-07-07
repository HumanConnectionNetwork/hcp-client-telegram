from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states


HUMAN_EVENT_LABELS = {
    "missing": "🚨 Persona desaparecida",
    "hospitalized": "🏥 Persona hospitalizada",
    "sheltered": "🏠 Persona refugiada / en albergue",
    "safe": "✅ Persona localizada / segura",
    "public_emergency": "🚑 Emergencia pública",
}


ANIMAL_SPECIES_LABELS = {
    "dog": "Perro",
    "cat": "Gato",
    "horse": "Caballo",
    "bird": "Ave",
    "unknown": "Animal",
}


ANIMAL_SIZE_LABELS = {
    "large": "Grande",
    "medium": "Mediano",
    "small": "Pequeño",
    "unknown": "Desconocido",
}


ANIMAL_BREED_LABELS = {
    "mixed": "Mestizo / Criollo",
    "unknown": "Desconocida",
}


ANIMAL_EVENT_LABELS = {
    "missing": "desaparecido",
    "hospitalized": "atendido",
    "sheltered": "resguardado",
    "safe": "localizado / seguro",
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


def get_event_label(context: ContextTypes.DEFAULT_TYPE) -> str:
    subject_type = context.user_data.get("subject_type", "human")
    event_type = context.user_data.get("event_type", "unknown")

    if subject_type == "animal":
        species = context.user_data.get("animal_species", "unknown")
        species_label = ANIMAL_SPECIES_LABELS.get(species, "Animal")
        event_label = ANIMAL_EVENT_LABELS.get(event_type, "reportado")
        return f"🐾 {species_label} {event_label}"

    return HUMAN_EVENT_LABELS.get(event_type, event_type)


def get_animal_breed_label(context: ContextTypes.DEFAULT_TYPE) -> str:
    breed = context.user_data.get("animal_breed", "unknown")
    return ANIMAL_BREED_LABELS.get(breed, breed)


def build_review_summary(context: ContextTypes.DEFAULT_TYPE) -> str:
    subject_type = context.user_data.get("subject_type", "human")
    source = context.user_data.get("source", "unknown")

    summary = (
        "📋 Revisa tu reporte antes de enviarlo\n\n"
        "Has completado la información disponible para este reporte.\n\n"
        "Este registro formará parte de un servicio humanitario abierto cuyo propósito "
        "es facilitar la búsqueda y relación de información durante situaciones de emergencia.\n\n"
        "Te pedimos enviar únicamente información que consideres verdadera o razonablemente confiable. "
        "Un reporte honesto puede ayudar a conectar información importante para otras personas.\n\n"
        "──────────────\n\n"
        f"Tipo de evento: {get_event_label(context)}\n"
    )

    if subject_type == "animal":
        species = context.user_data.get("animal_species", "unknown")
        size = context.user_data.get("animal_size", "unknown")

        summary += (
            f"Especie: {ANIMAL_SPECIES_LABELS.get(species, 'Animal')}\n"
            f"Tamaño: {ANIMAL_SIZE_LABELS.get(size, 'Desconocido')}\n"
            f"Raza aproximada: {get_animal_breed_label(context)}\n"
            f"Nombre reportado: {context.user_data.get('reported_name', 'Desconocido')}\n"
            f"Localización: {context.user_data.get('reported_location', 'Desconocido')}\n"
            f"Reportado por: {SOURCE_LABELS.get(source, source)}\n"
            f"Descripción: {context.user_data.get('description', 'Sin descripción')}\n\n"
        )
    else:
        summary += (
            f"Edad estimada: {context.user_data.get('estimated_age', 'Desconocido')}\n"
            f"Nombre reportado: {context.user_data.get('reported_name', 'Desconocido')}\n"
            f"Localización: {context.user_data.get('reported_location', 'Desconocido')}\n"
            f"Reportado por: {SOURCE_LABELS.get(source, source)}\n"
            f"Descripción: {context.user_data.get('description', 'Sin descripción')}\n\n"
        )

    summary += "¿Deseas enviar este reporte?"

    return summary


async def review_record(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    context.user_data["record_step"] = states.REVIEW

    keyboard = [
        [InlineKeyboardButton("✅ Confirmar y enviar", callback_data="review_confirm")],
        [InlineKeyboardButton("✏️ Editar información", callback_data="review_edit")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="review_cancel")],
    ]

    summary = build_review_summary(context)

    if update.message:
        await update.message.reply_text(
            summary,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if update.callback_query:
        await update.callback_query.edit_message_text(
            summary,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

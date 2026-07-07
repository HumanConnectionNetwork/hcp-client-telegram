from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.conversation import states
from app.conversation.create_record.review import review_record


EDIT_FIELD_KEY = "edit_field"


async def show_edit_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    subject_type = context.user_data.get("subject_type", "human")

    if subject_type == "animal":
        keyboard = [
            [InlineKeyboardButton("🐾 Especie", callback_data="edit_animal_species")],
            [InlineKeyboardButton("📏 Tamaño", callback_data="edit_animal_size")],
            [InlineKeyboardButton("🐕 Raza", callback_data="edit_animal_breed")],
            [InlineKeyboardButton("👤 Nombre", callback_data="edit_reported_name")],
            [InlineKeyboardButton("📍 Localización", callback_data="edit_reported_location")],
            [InlineKeyboardButton("📣 Fuente", callback_data="edit_source")],
            [InlineKeyboardButton("📝 Descripción", callback_data="edit_description")],
            [InlineKeyboardButton("⬅️ Volver al resumen", callback_data="edit_back_to_review")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="review_cancel")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🎂 Edad", callback_data="edit_estimated_age")],
            [InlineKeyboardButton("👤 Nombre", callback_data="edit_reported_name")],
            [InlineKeyboardButton("📍 Localización", callback_data="edit_reported_location")],
            [InlineKeyboardButton("📣 Fuente", callback_data="edit_source")],
            [InlineKeyboardButton("📝 Descripción", callback_data="edit_description")],
            [InlineKeyboardButton("⬅️ Volver al resumen", callback_data="edit_back_to_review")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="review_cancel")],
        ]

    await query.edit_message_text(
        text="✏️ ¿Qué información deseas editar?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_edit_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    choice = query.data.replace("edit_", "")

    if choice == "back_to_review":
        await review_record(update, context)
        return

    context.user_data[EDIT_FIELD_KEY] = choice

    if choice == "estimated_age":
        context.user_data["record_step"] = states.EDIT_TEXT
        await query.edit_message_text(
            text=(
                "🎂 Escribe la nueva edad estimada.\n\n"
                "Debe ser solo números.\n\n"
                "Ejemplo:\n"
                "45"
            )
        )
        return

    if choice == "reported_name":
        context.user_data["record_step"] = states.EDIT_TEXT
        await query.edit_message_text(
            text=(
                "👤 Escribe el nuevo nombre reportado.\n\n"
                "Si no lo sabes, escribe:\n"
                "Desconocido"
            )
        )
        return

    if choice == "reported_location":
        context.user_data["record_step"] = states.EDIT_TEXT
        await query.edit_message_text(
            text=(
                "📍 Escribe la nueva localización.\n\n"
                "Puedes escribir ciudad, barrio, hospital, refugio, clínica veterinaria "
                "o punto de referencia."
            )
        )
        return

    if choice == "description":
        context.user_data["record_step"] = states.EDIT_TEXT
        await query.edit_message_text(
            text=(
                "📝 Escribe la nueva descripción.\n\n"
                "Máximo 300 caracteres."
            )
        )
        return

    if choice == "source":
        await show_edit_source_options(update, context)
        return

    if choice == "animal_species":
        await show_edit_animal_species_options(update, context)
        return

    if choice == "animal_size":
        await show_edit_animal_size_options(update, context)
        return

    if choice == "animal_breed":
        await show_edit_animal_breed_options(update, context)
        return


async def show_edit_source_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    keyboard = [
        [InlineKeyboardButton("👨‍👩‍👧 Familia", callback_data="edit_source_family")],
        [InlineKeyboardButton("🏥 Hospital", callback_data="edit_source_hospital")],
        [InlineKeyboardButton("🚒 Bomberos", callback_data="edit_source_fire_department")],
        [InlineKeyboardButton("🤝 Voluntario", callback_data="edit_source_volunteer")],
        [InlineKeyboardButton("👮 Policía", callback_data="edit_source_police")],
        [InlineKeyboardButton("👤 Amigo / Conocido", callback_data="edit_source_friend")],
        [InlineKeyboardButton("❓ Desconocido", callback_data="edit_source_unknown")],
    ]

    await query.edit_message_text(
        text="📣 Selecciona la nueva fuente del reporte.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_edit_source(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    source = query.data.replace("edit_source_", "")
    context.user_data["source"] = source

    await review_record(update, context)


async def show_edit_animal_species_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    keyboard = [
        [InlineKeyboardButton("🐶 Perro", callback_data="edit_animal_species_dog")],
        [InlineKeyboardButton("🐱 Gato", callback_data="edit_animal_species_cat")],
        [InlineKeyboardButton("🐴 Caballo", callback_data="edit_animal_species_horse")],
        [InlineKeyboardButton("🐦 Ave", callback_data="edit_animal_species_bird")],
        [InlineKeyboardButton("🐾 Otro / No sé", callback_data="edit_animal_species_unknown")],
    ]

    await query.edit_message_text(
        text="🐾 Selecciona la nueva especie.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_edit_animal_species(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    species = query.data.replace("edit_animal_species_", "")
    context.user_data["animal_species"] = species

    await review_record(update, context)


async def show_edit_animal_size_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    keyboard = [
        [InlineKeyboardButton("🐕 Grande", callback_data="edit_animal_size_large")],
        [InlineKeyboardButton("🐕 Mediano", callback_data="edit_animal_size_medium")],
        [InlineKeyboardButton("🐕 Pequeño", callback_data="edit_animal_size_small")],
        [InlineKeyboardButton("❓ Desconocido", callback_data="edit_animal_size_unknown")],
    ]

    await query.edit_message_text(
        text="📏 Selecciona el nuevo tamaño aproximado.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_edit_animal_size(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    size = query.data.replace("edit_animal_size_", "")
    context.user_data["animal_size"] = size

    await review_record(update, context)


async def show_edit_animal_breed_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    keyboard = [
        [InlineKeyboardButton("🐕 De raza conocida", callback_data="edit_animal_breed_known")],
        [InlineKeyboardButton("🐕 Mestizo / Criollo", callback_data="edit_animal_breed_mixed")],
        [InlineKeyboardButton("❓ Desconocida", callback_data="edit_animal_breed_unknown")],
    ]

    await query.edit_message_text(
        text="🐾 Selecciona la nueva raza aproximada.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_edit_animal_breed(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    breed = query.data.replace("edit_animal_breed_", "")

    if breed == "known":
        context.user_data[EDIT_FIELD_KEY] = "animal_breed"
        context.user_data["record_step"] = states.ANIMAL_BREED_TEXT
        await query.edit_message_text(
            text=(
                "🐾 Escribe la nueva raza aproximada.\n\n"
                "Máximo 40 caracteres.\n\n"
                "Ejemplo:\n"
                "Golden Retriever"
            )
        )
        return

    context.user_data["animal_breed"] = breed

    await review_record(update, context)


async def handle_edit_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    if not update.message:
        return False

    step = context.user_data.get("record_step")

    if step not in [states.EDIT_TEXT, states.ANIMAL_BREED_TEXT]:
        return False

    text = update.message.text.strip()
    field = context.user_data.get(EDIT_FIELD_KEY)

    if step == states.ANIMAL_BREED_TEXT:
        if len(text) > 40:
            await update.message.reply_text(
                "⚠️ La raza debe tener máximo 40 caracteres.\n\n"
                "Intenta escribir una versión más corta."
            )
            return True

        context.user_data["animal_breed"] = text
        context.user_data["record_step"] = states.REVIEW
        await review_record(update, context)
        return True

    if field == "estimated_age":
        if not text.isdigit():
            await update.message.reply_text(
                "⚠️ La edad debe ser un número.\n\n"
                "Ejemplo:\n"
                "45"
            )
            return True

        context.user_data["estimated_age"] = text

    elif field == "reported_name":
        if len(text) > 80:
            await update.message.reply_text(
                "⚠️ El nombre debe tener máximo 80 caracteres."
            )
            return True

        context.user_data["reported_name"] = text

    elif field == "reported_location":
        if len(text) > 120:
            await update.message.reply_text(
                "⚠️ La localización debe tener máximo 120 caracteres."
            )
            return True

        context.user_data["reported_location"] = text

    elif field == "description":
        if len(text) > 300:
            await update.message.reply_text(
                "⚠️ La descripción debe tener máximo 300 caracteres."
            )
            return True

        context.user_data["description"] = text

    else:
        return False

    context.user_data["record_step"] = states.REVIEW
    await review_record(update, context)
    return True

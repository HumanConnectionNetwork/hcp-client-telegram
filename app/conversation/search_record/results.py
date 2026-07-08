from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


MOCK_RESULTS = [
    {
        "candidate_id": "candidate_1",
        "probability": 68,
        "event_type": "🚨 Persona desaparecida",
        "reported_name": "Luis Trapito",
        "estimated_age": "45",
        "reported_location": "La Guaira",
        "status": "Reportado",
        "source": "👤 Amigo / Conocido",
        "reason_summary": "Coinciden parcialmente el lugar y el contexto, pero el nombre y la edad no coinciden completamente.",
    },
    {
        "candidate_id": "candidate_2",
        "probability": 52,
        "event_type": "🏥 Persona hospitalizada",
        "reported_name": "Luis Trápito",
        "estimated_age": "45",
        "reported_location": "Hospital en Caracas",
        "status": "Reportado",
        "source": "🏥 Hospital",
        "reason_summary": "El nombre es parecido y la edad es compatible, pero la localización es diferente.",
    },
    {
        "candidate_id": "candidate_3",
        "probability": 35,
        "event_type": "🏠 Persona refugiada / en albergue",
        "reported_name": "Luis T.",
        "estimated_age": "Adulto",
        "reported_location": "Centro de refugio",
        "status": "Reportado",
        "source": "🤝 Voluntario",
        "reason_summary": "Existen pocos datos compatibles. Este resultado tiene baja probabilidad.",
    },
]


def get_mock_results_for_query(search_name: str) -> list[dict]:
    normalized_name = search_name.strip().lower()

    if normalized_name in ["mario", "pedro", "jose", "josé", "carlos"]:
        return [
            {
                "candidate_id": "weak_candidate_1",
                "probability": 28,
                "event_type": "🚨 Persona desaparecida",
                "reported_name": "Luis Trapito",
                "estimated_age": "45",
                "reported_location": "La Guaira",
                "status": "Reportado",
                "source": "👤 Amigo / Conocido",
                "reason_summary": "El nombre no coincide. Solo existen similitudes generales de contexto.",
            }
        ]

    return MOCK_RESULTS


async def show_mock_search_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    search_name = context.user_data.get("search_reported_name", "Desconocido")
    search_age = context.user_data.get("search_estimated_age", "Desconocido")
    search_location = context.user_data.get(
        "search_reported_location",
        "Desconocido",
    )
    search_recognition_features = context.user_data.get(
        "search_recognition_features",
        "No especificadas",
    )

    results = get_mock_results_for_query(search_name)

    message = (
        "🔍 Resultados de búsqueda\n\n"
        "HCP no identifica personas.\n"
        "Relaciona observaciones humanitarias que podrían corresponder a un mismo caso.\n\n"
        "Datos consultados:\n"
        f"👤 Nombre: {search_name}\n"
        f"🎂 Edad aproximada: {search_age}\n"
        f"📍 Localización: {search_location}\n"
        f"🆔 Características: {search_recognition_features}\n\n"
    )

    if not results:
        await update.message.reply_text(
            message
            + "No se encontraron observaciones compatibles con los datos ingresados."
        )
        return

    strong_results = [result for result in results if result["probability"] >= 60]

    if not strong_results:
        message += (
            "No se encontraron coincidencias fuertes.\n\n"
            "Sin embargo, existen algunos reportes con características parcialmente similares. "
            "Pueden ser útiles para verificación humanitaria, pero no deben interpretarse como coincidencias probables.\n\n"
        )
    else:
        message += "Se encontraron posibles casos relacionados:\n\n"

    keyboard = []

    for index, result in enumerate(results, start=1):
        message += (
            "──────────────\n"
            f"📄 Posible caso #{index}\n\n"
            f"Probabilidad: {result['probability']}%\n"
            f"Tipo: {result['event_type']}\n"
            f"Nombre reportado: {result['reported_name']}\n"
            f"Edad estimada: {result['estimated_age']}\n"
            f"Localización: {result['reported_location']}\n"
            f"Estado: {result['status']}\n"
            f"Fuente: {result['source']}\n\n"
            f"¿Por qué este resultado?\n{result['reason_summary']}\n\n"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Ver explicación #{index}",
                    callback_data=f"explain_{result['candidate_id']}",
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

    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

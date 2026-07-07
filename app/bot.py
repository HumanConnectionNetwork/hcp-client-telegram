from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.conversation.create_record import (
    ask_estimated_age,
    create_record_menu,
    handle_animal_breed,
    handle_animal_size,
    handle_animal_species,
    handle_record_text,
    handle_reporter_source,
    select_subject_type,
    submit_record,
)
from app.conversation.search_record import search_record_menu
from app.conversation.search_record.form import (
    ask_search_estimated_age,
    handle_search_text,
)
from app.conversation.start import start


def main() -> None:
    application = Application.builder().token(
        settings.telegram_bot_token
    ).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        CallbackQueryHandler(start, pattern="^(cancel|back_to_start)$")
    )

    application.add_handler(
        CallbackQueryHandler(create_record_menu, pattern="^create_report$")
    )

    application.add_handler(
        CallbackQueryHandler(search_record_menu, pattern="^search_report$")
    )

    application.add_handler(
        CallbackQueryHandler(select_subject_type, pattern="^subject_")
    )

    application.add_handler(
        CallbackQueryHandler(ask_estimated_age, pattern="^event_")
    )

    application.add_handler(
        CallbackQueryHandler(ask_search_estimated_age, pattern="^search_")
    )

    application.add_handler(
        CallbackQueryHandler(handle_animal_species, pattern="^animal_species_")
    )

    application.add_handler(
        CallbackQueryHandler(handle_animal_size, pattern="^animal_size_")
    )

    application.add_handler(
        CallbackQueryHandler(handle_animal_breed, pattern="^animal_breed_")
    )

    application.add_handler(
        CallbackQueryHandler(handle_reporter_source, pattern="^source_")
    )

    application.add_handler(
        CallbackQueryHandler(submit_record, pattern="^review_confirm$")
    )

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_record_text),
        group=1,
    )

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_text),
        group=2,
    )

    print("HCP Telegram Client is running...")

    application.run_polling()


if __name__ == "__main__":
    main()

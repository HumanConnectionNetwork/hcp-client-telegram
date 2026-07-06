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
    handle_record_text,
)
from app.conversation.start import start


def main() -> None:
    application = Application.builder().token(
        settings.telegram_bot_token
    ).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(
        CallbackQueryHandler(create_record_menu, pattern="^create_report$")
    )

    application.add_handler(
        CallbackQueryHandler(ask_estimated_age, pattern="^event_")
    )

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_record_text)
    )

    print("HCP Telegram Client is running...")

    application.run_polling()


if __name__ == "__main__":
    main()

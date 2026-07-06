from telegram.ext import Application, CommandHandler

from app.config import settings
from app.conversation.start import start


def main() -> None:
    application = Application.builder().token(
        settings.telegram_bot_token
    ).build()

    application.add_handler(CommandHandler("start", start))

    print("HCP Telegram Client is running...")

    application.run_polling()


if __name__ == "__main__":
    main()

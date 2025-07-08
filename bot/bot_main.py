from telegram.ext import Application, CommandHandler
from handlers.connect import connect_github
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command
    application.add_handler(CommandHandler("connect_github", connect_github))

    # Start bot with polling
    application.run_polling()

if __name__ == "__main__":
    main()

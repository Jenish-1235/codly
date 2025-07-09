from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from bot.handlers.connect import connect_github
from bot.handlers.list_repos import list_repos, handle_repo_pagination
from bot.handlers.create_issue import issue_conversation_handler
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command
    application.add_handler(CommandHandler("connect_github", connect_github))
    application.add_handler(CommandHandler("list_repos", list_repos))
    application.add_handler(CallbackQueryHandler(handle_repo_pagination, pattern=r"^repos:\d+:\d+$"))
    application.add_handler(issue_conversation_handler)
    # Start bot with polling
    application.run_polling()

if __name__ == "__main__":
    main()

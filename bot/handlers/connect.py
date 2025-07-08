from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

BACKEND_BASE_URL = "https://4c5c34e2f8a5.ngrok-free.app"  # Update if deployed

async def connect_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    auth_url = f"{BACKEND_BASE_URL}/start_auth?telegram_user_id={user_id}"

    keyboard = [
        [InlineKeyboardButton("🔗 Connect GitHub", url=auth_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please authenticate with GitHub to continue:",
        reply_markup=reply_markup
    )

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from core.github_client import get_user_repos
from db.user import get_user_token

ITEMS_PER_PAGE = 5

# shared memory for pagination state (or use TinyDB if needed)
pagination_cache = {}

def build_pagination_keyboard(page, total_pages, user_id):
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅ Prev", callback_data=f"repos:{user_id}:{page - 1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("Next ➡", callback_data=f"repos:{user_id}:{page + 1}"))
    return InlineKeyboardMarkup([buttons]) if buttons else None

async def list_repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_token(user_id)
    if not user_data:
        await update.message.reply_text("⚠️ Please authenticate with GitHub using /connect_github first.")
        return

    try:
        repos = await get_user_repos(user_data["access_token"])
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to fetch repos: {e}")
        return

    total_pages = max(1, (len(repos) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = 1
    pagination_cache[user_id] = repos

    await send_repo_page(update, context, user_id, page, total_pages)

async def send_repo_page(update, context, user_id, page, total_pages):
    repos = pagination_cache.get(user_id, [])
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_page_repos = repos[start:end]

    lines = [f"📦 Repositories (Page {page}/{total_pages}):"]
    for i, repo in enumerate(current_page_repos, start=start + 1):
        lines.append(f"{i}. {repo['full_name']}")

    keyboard = build_pagination_keyboard(page, total_pages, user_id)
    message_text = "\n".join(lines)

    if update.callback_query:
        # Called when a page button is pressed
        cb = update.callback_query
        await cb.message.edit_text(message_text, reply_markup=keyboard)
        await cb.answer()
    else:
        # Initial listing from /list_repos command
        await update.message.reply_text(message_text, reply_markup=keyboard)



async def handle_repo_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, user_id_str, page_str = query.data.split(":")
    user_id = int(user_id_str)
    page = int(page_str)

    repos = pagination_cache.get(user_id)
    if not repos:
        await query.answer("❗Session expired. Please use /list_repos again.", show_alert=True)
        return

    total_pages = max(1, (len(repos) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    await send_repo_page(update, context, user_id, page, total_pages)

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from core.github_client import get_user_repos, create_github_issue
from db.user import get_user_token

# FSM States
ASK_REPO, ASK_TITLE, ASK_DESCRIPTION = range(3)

# In-memory cache per user (can later move to Redis or DB)
issue_data_cache = {}

async def start_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = get_user_token(user_id)

    if not user_data:
        await update.message.reply_text("⚠️ Please connect GitHub first using /connect_github.")
        return ConversationHandler.END

    repos = await get_user_repos(user_data["access_token"])
    if not repos:
        await update.message.reply_text("❗ You don’t have any repositories to create issues in.")
        return ConversationHandler.END

    issue_data_cache[user_id] = {
        "repos": repos,
        "access_token": user_data["access_token"]
    }

    repo_lines = [f"{i+1}. {r['full_name']}" for i, r in enumerate(repos)]
    repo_lines.append(f"{len(repos)+1}. ➕ Create New Repo")

    await update.message.reply_text(
        "📁 Please select a repository by sending the number:\n\n" + "\n".join(repo_lines)
    )
    return ASK_REPO

async def receive_repo_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text.strip()

    if not choice.isdigit():
        await update.message.reply_text("❌ Please enter a valid number.")
        return ASK_REPO

    choice = int(choice)
    data = issue_data_cache.get(user_id)
    repos = data.get("repos", [])

    if choice < 1 or choice > len(repos) + 1:
        await update.message.reply_text("❌ Number out of range.")
        return ASK_REPO

    if choice == len(repos) + 1:
        await update.message.reply_text("🚧 Boom! Placeholder for creating a new repo. Coming soon.")
        return ConversationHandler.END

    selected_repo = repos[choice - 1]["full_name"]
    issue_data_cache[user_id]["repo"] = selected_repo

    await update.message.reply_text("📝 Please enter the *issue title*:", parse_mode="Markdown")
    return ASK_TITLE

async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    issue_data_cache[user_id]["title"] = update.message.text.strip()

    await update.message.reply_text("📄 Now enter the *issue description*:", parse_mode="Markdown")
    return ASK_DESCRIPTION

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = issue_data_cache.get(user_id)

    if not data:
        await update.message.reply_text("⚠️ Session expired. Please try again.")
        return ConversationHandler.END

    data["description"] = update.message.text.strip()

    try:
        issue = await create_github_issue(
            token=data["access_token"],
            repo=data["repo"],
            title=data["title"],
            body=data["description"]
        )
        await update.message.reply_text(
            f"✅ Issue created: [{issue['title']}]({issue['html_url']})",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to create issue:\n{e}")

    issue_data_cache.pop(user_id, None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    issue_data_cache.pop(update.effective_user.id, None)
    await update.message.reply_text("❌ Issue creation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

issue_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("create_issue", start_issue)],
    states={
        ASK_REPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_repo_choice)],
        ASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
        ASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
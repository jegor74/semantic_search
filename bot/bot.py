import requests
import json
import sys
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# ==== Configuration ====
BOT_TOKEN = "8867854461:AAGc9YEoQL5zKBWX_L-MuBN2LNDbPNVPXtU" 
API_URL = "http://127.0.0.1:8000/search" 


def search_documents(query: str, top_k: int = 3) -> list:
    """
    Calls searching API.

    Args:
    - query: user's question
    - top_k: number of relevant answers (default = 3)

    Returns:
    - list of chunks with metadata (text, source, distance)
    """

    try:
        response = requests.post(API_URL, json={"query": query, "top_k": top_k})
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])        # returning list of chunks or empty list
        else:
            return []                             # if status is not 200 - nothing found
    except Exception as e:
        print(f"Ошибка при вызове API: {e}")
        return []                                 # every error means empty result


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Processes /start command.

    Args:
    - update: information about query
    - context: data between different calls (unused)
    """

    if update.message is None:
        return

    await update.message.reply_text(
        "📚 Привет! Я бот для семантического поиска по книгам.\n"
        "Отправь мне любой вопрос, и я найду самые релевантные отрывки из моей базы книг."
    )


async def handle_message(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Processes text messages.

    Args:
    - update: information about query
    - context: data between different calls (unused)
    """
    
    if update.message is None or update.message.text is None:                        # if there is no message - exit
        return

    query = update.message.text.strip()                                              # getting query text
    if not query:
        await update.message.reply_text("Пожалуйста, напиши вопрос.")
        return

    await update.message.reply_text("🔍 Ищу...")                                     # notifying user that search is in progress

    results = search_documents(query, top_k=3)                                       # calling API

    if not results:
        await update.message.reply_text("😕 Ничего не найдено по вашему запросу.")
        return

    message = f"📖 *Результаты поиска по запросу:*\n_{query}_\n\n"                   # forming understandable message with results
    for i, chunk in enumerate(results, 1):
        text = chunk.get("text", "").strip()
        source = chunk.get("source", "Неизвестный источник")
        distance = chunk.get("distance", 0)
        if len(text) > 400:                                                          # truncating long chunks for readability
            text = text[:400] + "..."
        message += f"{i}. *{source}* (сходство: {distance * 100:.1f}% )\n"
        message += f"   {text}\n\n"

    if len(message) > 4096:                                                          # telegram message limit is 4096 chars - splitting if needed
        for x in range(0, len(message), 4096):
            await update.message.reply_text(message[x:x+4096], parse_mode="Markdown")
    else:
        await update.message.reply_text(message, parse_mode="Markdown")


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()                               # making app for bot

    application.add_handler(CommandHandler("start", start))                                    # register command handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))   # register message handler

    print("🤖 Bot is avaiable. Press Ctrl+C for exit.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)                                  # running bot


if __name__ == "__main__":
    main()

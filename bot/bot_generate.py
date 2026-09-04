import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))            # adding root directory to the module search path (so we can import src/)


import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.llm_generator import generate_answer
from src.config import API_URL, BOT_TOKEN


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Add it to the root .env file."
    )


def truncate_by_sentence(text: str, max_len: int = 400) -> str:
    """
    Truncates text by sentences, so text ends with (. ! ? ; : ... ?!).
    Or text ends with ... if truncate was forced.

    Args:
    - text: model's answer
    - max_len: max length of text (default = 400)

    Returns:
    - truncated string ending with a sentence delimiter or original text if it's shorter than max_len.
    """

    if len(text) <= max_len:                                    # returning text if it's already short enough
        return text

    truncate_pos = max_len                                      # start truncation at max_len
    for sep in [". ", "! ", "? ", "; ", ": ", "... ", "?! "]:
        pos = text.rfind(sep, 0, max_len)                       # search for separator from the end, up to max_len
        if pos != -1:                                           # if found
            truncate_pos = min(truncate_pos, pos + len(sep))    # cut after the separator and the trailing space
    
    if truncate_pos == max_len:                                 # forced truncating if there are no separators found
        return text[:max_len].strip() + "..."
    return text[:truncate_pos].strip()                          # cut the text at the found position, remove trailing spaces


def search_documents(query: str, top_k: int = 5) -> list:
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
        "Отправь мне любой вопрос, и я сформулирую ответ на основе моей базы книг."
    )


async def handle_message(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Processes text messages.

    Args:
    - update: information about query
    - context: data between different calls (unused)
    """
    
    if update.message is None or update.message.text is None:                               # if there is no message - exit
        return

    query = update.message.text.strip()                                                     # getting query text
    if not query:
        await update.message.reply_text("Пожалуйста, напиши вопрос.")
        return

    await update.message.reply_text("🔍 Ищу...")                                            # notifying user that search is in progress

    results = search_documents(query, top_k=5)                                              # calling API

    if not results:
        await update.message.reply_text("😕 Ничего не найдено по вашему запросу.")
        return

    answer = generate_answer(query, results)                                                # making answers from top-3 chunks

    message = f"🧠 *Ответ:*\n{answer}\n\n"                                                  # forming understandable message with results
    message += "📚 *Источники:*\n"
    for i, chunk in enumerate(results, 1):
        message += f"{i}. {chunk["source"]} (сходство: {chunk["distance"] * 100:.1f}% )\n"
    
    
    if len(message) > 4096:                                                                 # telegram message limit is 4096 chars - splitting if needed
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

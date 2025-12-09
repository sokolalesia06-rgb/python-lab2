import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не знайдено. Додай його у .env")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я робочий бот. Введи /menu щоб побачити команди.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 Доступні команди:\n"
        "/menu - показати це меню\n"
        "/scream <текст> - відправити текст великими літерами\n"
        "/whisper <user_id|@username|reply> <текст> - приватне повідомлення\n\n"
        "Якщо хочеш надіслати собі — знайди свій user_id через @userinfobot."
    )
    await update.message.reply_text(text)

async def scream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Використання: /scream <текст>")
        return
    msg = " ".join(context.args).upper()
    await update.message.reply_text(msg)

async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /whisper <user_id|@username> <message>
    або у відповідь на чийсь меседж: /whisper reply <message>  (тобі потрібно відповісти на повідомлення користувача і написати /whisper reply текст)
    Бот зможе надіслати повідомлення лише тим, хто починав діалог з ботом або має публічний username і дозволяє повідомлення.
    """
    if context.args and context.args[0].lower() == "reply":
        if not update.message.reply_to_message:
            await update.message.reply_text("Щоб використати 'reply', потрібно виконати команду як відповідь на повідомлення користувача.")
            return
        target_id = update.message.reply_to_message.from_user.id
        message = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        if not message:
            await update.message.reply_text("Напиши текст для надсилання.")
            return
        try:
            await context.bot.send_message(chat_id=target_id, text=message)
            await update.message.reply_text("Повідомлення надіслано (reply).")
        except Exception as e:
            logger.exception("Помилка при whisper (reply): %s", e)
            await update.message.reply_text("Не вдалося надіслати повідомлення (reply).")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Використання: /whisper <user_id|@username> <повідомлення>\nабо /whisper reply <повідомлення> як відповідь на повідомлення.")
        return

    target = context.args[0]
    message = " ".join(context.args[1:])

    if target.startswith("@"):
        try:
            chat = await context.bot.get_chat(target)  # може зловитись помилкою, якщо username недійсний
            target_id = chat.id
        except Exception as e:
            logger.warning("Не вдалося знайти username %s: %s", target, e)
            await update.message.reply_text(f"Не вдалося знайти користувача {target}. Користувач може не мати публічного username або не починав діалог з ботом.")
            return
    else:
        try:
            target_id = int(target)
        except ValueError:
            await update.message.reply_text("Невірний user_id. Вкажи числовий id або @username.")
            return

    try:
        await context.bot.send_message(chat_id=target_id, text=message)
        await update.message.reply_text("Повідомлення надіслано у приватний чат.")
    except Exception as e:
        logger.exception("Не вдалося надіслати whisper: %s", e)
        await update.message.reply_text(
            "Не вдалося надіслати повідомлення. Можливі причини:\n"
            "- користувач не починав діалог з ботом;\n"
            "- користувач заблокував бота;\n"
            "- неправильний id або username."
        )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Невідома команда. Використай /menu для списку команд.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("scream", scream))
    app.add_handler(CommandHandler("whisper", whisper))

    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Бот запущено...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

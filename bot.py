import logging
import os
from dotenv import load_dotenv

from telegram.ext import Updater, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Add it to .env")



def start(update, context):
    update.message.reply_text(
        "Привіт! Використай /menu щоб побачити доступні команди."
    )

def menu(update, context):
    update.message.reply_text(
        "📌 Доступні команди:\n"
        "/menu – показати меню\n"
        "/scream <text> – написати текст ВЕЛИКИМИ ЛІТЕРАМИ\n"
        "/whisper <user_id> <text> – надіслати приватне повідомлення\n"
    )

def scream(update, context):
    if not context.args:
        update.message.reply_text("Використання: /scream <текст>")
        return

    update.message.reply_text(" ".join(context.args).upper())

def whisper(update, context):
    """
    Надсилання приватного повідомлення іншому користувачу.
    ⚠️ Бот може написати лише тому, хто вже натиснув /start боту!
    """

    if len(context.args) < 2:
        update.message.reply_text(
            "Використання: /whisper <user_id> <повідомлення>"
        )
        return

    user_id = context.args[0]
    message = " ".join(context.args[1:])

    try:
        user_id = int(user_id)
    except ValueError:
        update.message.reply_text("user_id має бути числом.")
        return

    try:
        context.bot.send_message(chat_id=user_id, text=message)
        update.message.reply_text("Повідомлення надіслано!")
    except Exception as e:
        logger.error(e)
        update.message.reply_text(
            "❗ Не вдалося надіслати повідомлення.\n"
            "Причини:\n"
            "– користувач не писав боту;\n"
            "– bot заблокований;\n"
            "– неправильний user_id."
        )


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CommandHandler("scream", scream))
    dp.add_handler(CommandHandler("whisper", whisper))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

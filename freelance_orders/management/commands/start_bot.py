import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет")


def echo(update, context):
    text = 'ECHO: ' + update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


class Command(BaseCommand):
    env = Env()
    env.read_env()
    tg_token = env("BOT_TOKEN")
    tg_bot = telegram.Bot(token=tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()

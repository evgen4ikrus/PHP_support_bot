import telegram
from django.core.management.base import BaseCommand
from environs import Env

from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, InlineQueryHandler)

from bots.bot_helpers import handle_customer_message, handle_users_reply


class Command(BaseCommand):
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_BOT_TOKEN')
    tg_bot = telegram.Bot(token=tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(InlineQueryHandler(handle_customer_message))

    updater.start_polling()
    updater.idle()

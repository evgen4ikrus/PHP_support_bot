from .main_handler import get_bot_handler

from telegram.ext import Updater

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        telegram_bot_token = settings.TELEGRAM_BOT_TOKEN

        updater = Updater(telegram_bot_token)

        dispatcher = updater.dispatcher

        conv_handler = get_bot_handler()

        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()

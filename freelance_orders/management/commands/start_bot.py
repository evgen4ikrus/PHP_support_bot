import telegram

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackContext
from environs import Env
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def start(self, update: Update, context: CallbackContext) -> None:
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\!',
            reply_markup=ForceReply(selective=True),
        )

    def help_command(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Help!')

    def echo(self, update: Update, context: CallbackContext) -> None:
        custom_keyboard = [['Сделать заказ', 'Взять заказ']]
        reply_markup = telegram.ReplyKeyboardMarkup(
            custom_keyboard, resize_keyboard=True
        )
        update.message.reply_text(
            update.message.text, reply_markup=reply_markup
        )

    def handle(self, *args, **options):
        env = Env()
        env.read_env()
        telegram_bot_token = settings.TELEGRAM_BOT_TOKEN

        updater = Updater(telegram_bot_token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help_command))

        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, self.echo)
        )
        updater.start_polling()
        updater.idle()

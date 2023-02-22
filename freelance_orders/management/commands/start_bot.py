import logging

# import telegram

from telegram import Update, ForceReply
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackContext, RegexHandler,  ConversationHandler
from environs import Env

from django.core.management.base import BaseCommand
from django.conf import settings


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def start(self, update: Update, context: CallbackContext) -> None:
        reply_keyboard = [['Сделать заказ', 'Взять заказ']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Привет, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return 1

    def first(self, update: Update, context: CallbackContext) -> None:
        reply_keyboard = [['Мои заказы', 'Регистрация'], ['Назад']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Ты на странице подрядчика, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return 2

    def get_orders(self, update: Update, context: CallbackContext) -> None:
        reply_keyboard = [['Заказ 1', 'Заказ 2'], ['Назад']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Ты на странице заказов, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return 3

    def register(self, update: Update, context: CallbackContext) -> None:
        reply_keyboard = [['Назад']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Ты на странице регистрации, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return 3

    def handle(self, *args, **options):
        env = Env()
        env.read_env()
        telegram_bot_token = settings.TELEGRAM_BOT_TOKEN

        updater = Updater(telegram_bot_token)

        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                1: [
                    RegexHandler('^(Взять заказ)$', self.first),
                    RegexHandler('^(Сделать заказ)$', self.first)
                ],
                2: [
                    RegexHandler('^(Мои заказы)$', self.get_orders),
                    RegexHandler('^(Регистрация)$', self.register),
                    RegexHandler('^(Назад)$', self.start),
                ],
                3: [
                    RegexHandler('^(Мои заказы)$', self.first),
                    RegexHandler('^(Регистрация)$', self.register),
                    RegexHandler('^(Назад)$', self.first),
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
            )

        dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(CommandHandler('start', conv_handler))
        dispatcher.add_error_handler(self.error)
        updater.start_polling()
        updater.idle()

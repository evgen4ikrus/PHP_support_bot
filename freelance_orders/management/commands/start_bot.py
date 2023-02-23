import logging
from textwrap import dedent

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


FIRSTNAME, LASTNAME, PHONENUMBER = range(10, 13)


class Command(BaseCommand):
    def info(self, update: Update, context: CallbackContext) -> None:
        message = 'Здесь информация о нашей компании'
        update.message.reply_text(
            message
        )

    def customer(self, update: Update, context: CallbackContext) -> None:
        message = 'Здесь информация для заказчиков'
        update.message.reply_text(
            message
        )

    def performer(self, update: Update, context: CallbackContext) -> None:
        message = 'Здесь информация для исполнителей'
        update.message.reply_text(
            message
        )

    def tariff(self, update: Update, context: CallbackContext) -> None:
        message = 'Здесь информация о наших тарифах'
        update.message.reply_text(
            message
        )

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
        reply_keyboard = [['Мои заказы', 'Регистрация'], ['Назад', 'Закрыть']]
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
        reply_keyboard = [
            [
                'Заказ 1',
                'Заказ 2',
                'Заказ 3',
                'Заказ 4',
                'Заказ 5'
            ],
            ['Назад']
        ]
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
        message = 'Введите ваше имя:'

        update.message.reply_text(
            message
        )

        return FIRSTNAME

    def get_firstname(self, update: Update, context: CallbackContext):
        context.user_data[FIRSTNAME] = update.message.text
        message = 'Введите вашу фамилию:'

        update.message.reply_text(
            message
        )

        return LASTNAME

    def get_lastname(self, update: Update, context: CallbackContext):
        context.user_data[LASTNAME] = update.message.text
        message = 'Введите ваш номер телефона:'

        update.message.reply_text(
            message
        )

        return PHONENUMBER

    def get_phonenumber(self, update: Update, context: CallbackContext):
        reply_keyboard = [['Меню']]
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        context.user_data[PHONENUMBER] = update.message.text
        message = f'''\
            Регистрация завершена!
            Ваше имя: {context.user_data[FIRSTNAME]}
            Ваша фамилия: {context.user_data[LASTNAME]}
            Ваш номер телефона: {context.user_data[PHONENUMBER]}
        '''

        message = dedent(message)

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return 2

    def cancel(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text(
            'Счастливо! Будем рады помочь вам.'
        )

        return ConversationHandler.END

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
                    RegexHandler('^(Закрыть)$', self.cancel),
                    RegexHandler('^(Меню)$', self.start)
                ],
                3: [
                    RegexHandler('^(Мои заказы)$', self.get_orders),
                    RegexHandler('^(Регистрация)$', self.register),
                    RegexHandler('^(Назад)$', self.first),
                ],
                FIRSTNAME: [
                    MessageHandler(Filters.all, self.get_firstname, pass_user_data=True),
                ],
                LASTNAME: [
                    MessageHandler(Filters.all, self.get_lastname, pass_user_data=True),
                ],
                PHONENUMBER: [
                    MessageHandler(Filters.all, self.get_phonenumber, pass_user_data=True),
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CommandHandler('info', self.info))
        dispatcher.add_handler(CommandHandler('customer', self.customer))
        dispatcher.add_handler(CommandHandler('performer', self.performer))
        dispatcher.add_handler(CommandHandler('tariff', self.tariff))
        updater.start_polling()
        updater.idle()

import os

import redis
import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

_database = None


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('DATABASE_PASSWORD')
        database_host = os.getenv('DATABASE_HOST')
        database_port = os.getenv('DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=int(database_port), password=database_password)
    return _database


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(f'telegram_{chat_id}').decode('utf-8')

    states_functions = {
        'START': start,
        'MENU': handle_general_menu,
        'CUSTOMER_MENU': handle_customer_menu,
        'FREELANCER_MENU': handle_freelancer_menu,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(f'telegram_{chat_id}', next_state)


# я буду обрабатывать меню заказчика
def handle_customer_menu(bot, update):
    pass


# я буду обрабатывать меню фрилансера
def handle_freelancer_menu(bot, update):
    pass


# я буду определять пользователь кликнул на Заказчик или Фрилансер
def handle_general_menu(bot, update):
    query = update.callback_query
    if query.data == 'Заказчик':
        keyboard = [
            [InlineKeyboardButton('Сделать заказ', callback_data='Сделать заказ')],
            [InlineKeyboardButton('Что-то еще', callback_data='Что-то еще')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(text='меню заказчика', chat_id=query.message.chat_id, reply_markup=reply_markup)
        return 'CUSTOMER_MENU'
    elif query.data == 'Фрилансер':
        keyboard = [
            [InlineKeyboardButton('Найти заказ', callback_data='Найти заказ')],
            [InlineKeyboardButton('Что-то еще', callback_data='Что-то еще')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(text='меню заказчика', chat_id=query.message.chat_id, reply_markup=reply_markup)
        return 'FREELANCER_MENU'


def start(bot, update):
    user = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton('Я заказчик', callback_data='Заказчик')],
        [InlineKeyboardButton('Я фрилансер', callback_data='Фрилансер')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f'Привет, {user}'
    update.message.reply_text(text=message, reply_markup=reply_markup)
    return 'MENU'


class Command(BaseCommand):
    env = Env()
    env.read_env()
    tg_token = env("BOT_TOKEN")
    tg_bot = telegram.Bot(token=tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()

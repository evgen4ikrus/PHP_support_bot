import os

import redis
import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, CallbackContext)

from auth2.models import Freelancer
from freelance_orders.keyboards import get_freelancer_menu_keyboard, get_freelancer_orders_keyboard

_database = None


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('DATABASE_PASSWORD')
        database_host = os.getenv('DATABASE_HOST')
        database_port = os.getenv('DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=int(database_port), password=database_password)
    return _database


def handle_users_reply(update: Update, context: CallbackContext):
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
        'FREELANCER_ORDERS': handle_freelancer_orders,
        'FREELANCER_ORDER_DESCRIPTION': handle_freelancer_order_description,
        'CURRENT_FREELANCER_ORDERS': handle_current_freelancer_orders,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(f'telegram_{chat_id}', next_state)


# я буду обрабатывать меню заказчика
def handle_customer_menu(update: Update, context: CallbackContext):
    pass


def handle_current_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Назад':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню фрилансера:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'


def handle_freelancer_order_description(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Взять в работу':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Вы взяли КАКОЙ-ТО заказ в работу:', reply_markup=reply_markup,
                                 chat_id=query.message.chat_id)
        context.bot.send_message(text='Меню фрилансера:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    if query.data == 'Назад':
        keyboard = get_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDERS'


def handle_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Вернуться в меню':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Здесь будет описание заказа:'
        context.bot.send_message(message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    if query.data == 'Заказ':
        keyboard = [
            [InlineKeyboardButton('Взять в работу', callback_data='Взять в работу')],
            [InlineKeyboardButton('Назад', callback_data='Назад')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Здесь будет описание заказа:'
        context.bot.send_message(message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDER_DESCRIPTION'


def handle_freelancer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Найти заказ':
        keyboard = get_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDERS'
    if query.data == 'Выполняемые заказы':
        keyboard = [
            [InlineKeyboardButton('Назад', callback_data='Назад')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Здесь будут выполняемые заказы:'
        context.bot.send_message(message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CURRENT_FREELANCER_ORDERS'


# я буду определять пользователь кликнул на Заказчик или Фрилансер
def handle_general_menu(update: Update, context: CallbackContext):
    user_name = update.effective_user.first_name
    query = update.callback_query
    if query.data == 'Заказчик':
        keyboard = [
            [
                InlineKeyboardButton('Сделать заказ', callback_data='Сделать заказ'),
                InlineKeyboardButton('Что-то еще', callback_data='Что-то еще')
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Меню заказчика:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_MENU'
    elif query.data == 'Фрилансер':
        freelancer, _ = Freelancer.objects.get_or_create(tg_chat_id=query.message.chat_id)
        if freelancer.is_active:
            keyboard = get_freelancer_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'Меню фрилансера:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'FREELANCER_MENU'
        message = fr'{user_name}, в ближайшие 10 минут в Вами свяжется наш менеджер'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'START'


def start(update: Update, context: CallbackContext):
    user = update.effective_user.first_name
    keyboard = [
        [
            InlineKeyboardButton('Я заказчик', callback_data='Заказчик'),
            InlineKeyboardButton('Я фрилансер', callback_data='Фрилансер')
        ],
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

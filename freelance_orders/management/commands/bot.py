import os

import redis
import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, CallbackContext)

from auth2.models import Freelancer, User
from freelance_orders.keyboards import get_freelancer_menu_keyboard, get_freelancer_orders_keyboard, get_start_keyboard, \
    get_freelancer_current_orders_keyboard, get_menu_freelancer_orders_keyboard
from jobs.models import Job

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
        'ORDER_SEARCH': handle_order_search,
        'FREELANCER_ORDER_DESCRIPTION': handle_freelancer_order_description,
        'FREELANCER_ORDERS': handle_freelancer_orders,
        'MENU_FREELANCER_ORDERS': handle_menu_freelancer_orders
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(f'telegram_{chat_id}', next_state)


# я буду обрабатывать меню заказчика
def handle_customer_menu(update: Update, context: CallbackContext):
    pass


def handle_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    if command == 'Назад':
        keyboard = get_menu_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Ваши заказы:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU_FREELANCER_ORDERS'


def handle_menu_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Назад':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    freelancer = User.objects.get(tg_chat_id=query.message.chat_id)
    if query.data == 'Текущие заказы':
        orders = freelancer.jobs.filter(status='IN_PROGRESS')
        message = 'Текущие заказы:'
    elif query.data == 'Выполненные заказы':
        orders = freelancer.jobs.filter(status='DONE')
        message = 'Выполненные заказы:'
    if not orders:
        message = 'Нет заказов'
    keyboard = get_freelancer_current_orders_keyboard(orders)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'FREELANCER_ORDERS'


def handle_freelancer_order_description(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    if command == 'Взять в работу':
        order = Job.objects.get(id=order_id)
        freelancer = User.objects.get(tg_chat_id=query.message.chat_id)
        order.freelancer = freelancer
        order.status = 'IN_PROGRESS'
        order.save()
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=f'Вы взяли в работу заказ: {order.title}', chat_id=query.message.chat_id)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    elif command == 'Назад':
        freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
        page = freelancer.get_job_list()
        keyboard = get_freelancer_orders_keyboard(page)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'


def handle_order_search(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    if command == 'Вернуться в меню':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Здесь будет описание заказа:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    if command == 'Заказ':
        order = Job.objects.get(id=order_id)
        keyboard = [
            [InlineKeyboardButton('Взять в работу', callback_data=f'Взять в работу;{order.id}')],
            [InlineKeyboardButton('Назад', callback_data='Назад;')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f'{order.title}\n\n{order.description}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDER_DESCRIPTION'


def handle_freelancer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Найти заказ':
        freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
        page = freelancer.get_job_list()
        keyboard = get_freelancer_orders_keyboard(page)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'
    if query.data == 'Мои заказы':
        keyboard = get_menu_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Ваши заказы:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU_FREELANCER_ORDERS'


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
            message = 'Меню:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'FREELANCER_MENU'
        message = fr'{user_name}, в ближайшие 10 минут в Вами свяжется наш менеджер'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'START'


def start(update: Update, context: CallbackContext):
    user = update.effective_user.first_name
    keyboard = get_start_keyboard()
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

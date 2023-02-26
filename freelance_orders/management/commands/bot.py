import os

import redis
import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, CallbackContext)

from auth2.models import Freelancer, Client
from freelance_orders.client_branch_handlers import handle_customer_menu, handle_order_creation, \
    handle_customer_orders_menu, handle_customer_orders, handle_current_customer_order, handle_subscriptions, \
    handle_description_adding
from freelance_orders.freelancer_branch_handlers import handle_freelancer_menu, handle_order_search, \
    handle_freelancer_order_description, handle_freelancer_orders, handle_menu_freelancer_orders, \
    handle_current_freelancer_order
from freelance_orders.keyboards import get_freelancer_menu_keyboard, get_start_keyboard, get_client_menu_keyboard

_database = None


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('REDIS_DATABASE_PASSWORD')
        database_host = os.getenv('REDIS_DATABASE_HOST')
        database_port = os.getenv('REDIS_DATABASE_PORT')
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
        'MENU_FREELANCER_ORDERS': handle_menu_freelancer_orders,
        'CURRENT_FREELANCER_ORDER': handle_current_freelancer_order,
        'CREATE_ORDER': handle_order_creation,
        'DESCRIPTION_ADDING': handle_description_adding,
        'CUSTOMER_ORDERS_MENU': handle_customer_orders_menu,
        'CUSTOMER_ORDERS': handle_customer_orders,
        'CURRENT_CUSTOMER_ORDER': handle_current_customer_order,
        'SUBSCRIPTIONS': handle_subscriptions,
        'HANDLE_USERS_REPLY': handle_users_reply,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(f'telegram_{chat_id}', next_state)


def handle_general_menu(update: Update, context: CallbackContext):
    user_name = update.effective_user.first_name
    query = update.callback_query
    if query.data == 'Заказчик':
        Client.objects.get_or_create(tg_chat_id=query.message.chat_id)
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Меню:'
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
        message = f'{user_name}, в ближайшие 10 минут в Вами свяжется наш менеджер.\n' \
                  f'После разговора с менеджером нажмите `/start`.'
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
    tg_token = env('TELEGRAM_BOT_TOKEN')
    tg_bot = telegram.Bot(token=tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()
    updater.idle()

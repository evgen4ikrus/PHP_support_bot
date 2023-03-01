import os
import redis

from bots.keyboards import get_start_keyboard
from telegram import InlineKeyboardMarkup

_database = None


def display_private_access(update, context):
    keyboard = get_start_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = 'Попробуйте ещё раз:'
    closed_access_message = 'Доступ к приложению закрыт. Обратитесь к нашему менеджеру.'
    if update.message:
        update.message.reply_text(text=closed_access_message)
        update.message.reply_text(text=message, reply_markup=reply_markup)
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
        context.bot.send_message(text=closed_access_message, chat_id=chat_id)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=chat_id)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('REDIS_DATABASE_PASSWORD')
        database_host = os.getenv('REDIS_DATABASE_HOST')
        database_port = os.getenv('REDIS_DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=int(database_port), password=database_password)
    return _database

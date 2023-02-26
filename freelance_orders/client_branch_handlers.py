from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from auth2.models import User
from freelance_orders.keyboards import get_client_menu_keyboard, get_customer_orders_menu_keyboard
from jobs.models import Job


def handle_customer_orders_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Назад':
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Меню:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_MENU'


def handle_customer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Оставить заявку':
        message = 'Примеры заявок:\n' \
                  'Нужно добавить в интернет-магазин фильтр товаров по цвету\n' \
                  'Нужно выгрузить товары с сайта в Excel-таблице\nНужно загрузить 450 SKU на сайт из Execel таблицы\n\n' \
                  'Введите название вашей заявки в поле для ввода:'
        keyboard = [
            [InlineKeyboardButton('Отменить', callback_data='Отменить')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CREATE_ORDER'
    if query.data == 'Мои заявки':
        message = 'Ваши заявки'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'


def handle_order_creation(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        chat_id = query.message.chat_id
    else:
        chat_id = update.message.chat_id
        order_text = update.message.text
        client = User.objects.get(tg_chat_id=chat_id)
        Job.objects.create(title=order_text, client=client)
    keyboard = get_client_menu_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = 'Меню:'
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=chat_id)
    return 'CUSTOMER_MENU'

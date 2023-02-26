from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from auth2.models import Freelancer
from auth2.models import User
from freelance_orders.keyboards import get_freelancer_menu_keyboard, get_menu_freelancer_orders_keyboard, \
    get_freelancer_current_orders_keyboard, get_freelancer_orders_keyboard
from jobs.models import Job


def handle_current_freelancer_order(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    order = Job.objects.get(id=order_id)
    if command == 'Написать заказчику':
        # TODO: сделать чат с заказчиком
        pass
    elif command == 'Заказ выполнен':
        order.status = 'DONE'
        order.save()
        context.bot.send_message(text=f'Вы подтвердили выполнение заказа: {order.title}', chat_id=query.message.chat_id)
    keyboard = get_menu_freelancer_orders_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = 'Ваши заказы:'
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'MENU_FREELANCER_ORDERS'


def handle_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    command, payload = query.data.split(';')
    if command == 'Назад':
        keyboard = get_menu_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Ваши заказы:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU_FREELANCER_ORDERS'
    status, order_id = payload.split(':')
    order = Job.objects.get(id=order_id)
    message = f'{order.title}\n\n{order.description}'
    keyboard = [
        [InlineKeyboardButton('Написать заказчику', callback_data=f'Написать заказчику;{order.id}')],
    ]
    if status == 'IN_PROGRESS':
        keyboard.append(
            [InlineKeyboardButton('Подтвердить выполнение заказа', callback_data=f'Заказ выполнен;{order.id}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data=f'Назад;{order.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'HANDLE_CURRENT_FREELANCER_ORDERS'


def handle_menu_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Назад':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    freelancer = User.objects.get(tg_chat_id=query.message.chat_id)
    if query.data == 'Текущие заказы':
        status = 'IN_PROGRESS'
        orders = freelancer.jobs.filter(status=status)
        message = 'Текущие заказы:'
    else:
        status = 'DONE'
        orders = freelancer.jobs.filter(status=status)
        message = 'Выполненные заказы:'
    if not orders:
        message = 'Нет заказов'
    keyboard = get_freelancer_current_orders_keyboard(orders, status)
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
        keyboard = get_freelancer_orders_keyboard(freelancer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'


def handle_order_search(update: Update, context: CallbackContext):
    query = update.callback_query
    command, payload = query.data.split(';')
    if command == 'Вернуться в меню':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Меню:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    elif command == 'Заказ':
        order_id = payload
        order = Job.objects.get(id=order_id)
        keyboard = [
            [InlineKeyboardButton('Взять в работу', callback_data=f'Взять в работу;{order.id}')],
            [InlineKeyboardButton('Назад', callback_data='Назад;')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f'{order.title}\n\n{order.description}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDER_DESCRIPTION'
    elif command == 'Показать ещё':
        freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
        page = payload
        keyboard = get_freelancer_orders_keyboard(freelancer, page_num=page)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'


def handle_freelancer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'Найти заказ':
        freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
        keyboard = get_freelancer_orders_keyboard(freelancer)
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

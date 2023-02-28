import os

import redis
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from auth2.models import Client
from freelance_orders.keyboards import get_client_menu_keyboard, get_customer_orders_menu_keyboard, \
    get_freelancer_current_orders_keyboard, get_start_keyboard
from jobs.models import Job
from products.models import Subscription

_database = None


def handle_freelancer_message(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        command, freelancer_chat_id = query.data.split(';')
        if command == 'Ответить':
            message = 'Напишите ответ в поле для ввода:'
            context.user_data['freelancer_chat_id'] = freelancer_chat_id
            context.bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'HANDLE_FREELANCER_MESSAGE'
    if update.message:
        freelancer_chat_id = context.user_data['customer_chat_id']
        answer = f'Вам пришел ответ от заказчика:\n\n<b>{update.message.text}</b>'
        context.bot.send_message(text='Ответ отправлен', chat_id=update.message.chat_id)
        context.bot.send_message(text=answer, chat_id=freelancer_chat_id, parse_mode="html")
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=update.message.chat_id)
        return 'CUSTOMER_MENU'


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('REDIS_DATABASE_PASSWORD')
        database_host = os.getenv('REDIS_DATABASE_HOST')
        database_port = os.getenv('REDIS_DATABASE_PORT')
        _database = redis.Redis(host=database_host, port=int(database_port), password=database_password)
    return _database


def display_private_access(update, context):
    keyboard = get_start_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f'Попробуйте ещё раз:'
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


def handle_sending_messages_to_freelancer(update: Update, context: CallbackContext):
    if update.message:
        text = update.message.text
        if text:
            db = get_database_connection()
            order_id = context.user_data['order_id']
            order = Job.objects.get(id=order_id)
            message = f'Вам пришло сообщение от заказчика, по заказу "{order.title}":\n\n' \
                      f'<b>{text}</b>'
            keyboard = [[InlineKeyboardButton('Ответить', callback_data=f'Ответить;{update.message.chat_id}')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            db.set(f'telegram_{order.freelancer.tg_chat_id}', 'HANDLE_CUSTOMER_MESSAGE')
            context.bot.send_message(text=message, chat_id=order.freelancer.tg_chat_id, reply_markup=reply_markup,
                                     parse_mode="html")
            keyboard = [[InlineKeyboardButton('Вернуться в меню заказов', callback_data='Вернуться в меню заказов')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text='Сообщение отправлено фрилансеру', reply_markup=reply_markup,
                                     chat_id=update.message.chat_id)
            return 'SENDING_MESSAGES_TO_FREELANCER'
    query = update.callback_query
    if query:
        if query.data == 'Вернуться в меню заказов':
            message = 'Ваши заказы'
            keyboard = get_customer_orders_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'CUSTOMER_ORDERS_MENU'


def handle_description_adding(update: Update, context: CallbackContext):
    if update.message:
        text = update.message.text
        if text:
            chat_id = update.message.chat_id
            client = Client.objects.get(tg_chat_id=chat_id)
            Job.objects.create(title=context.user_data['order_title'], client=client, description=text)
            message = 'Заказ создан. Вы можете его увидеть в разделе "Мои заказы"'
            context.bot.send_message(text=message, chat_id=chat_id)
            keyboard = get_client_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=chat_id)
            return 'CUSTOMER_MENU'


def handle_subscriptions(update, context):
    query = update.callback_query
    command, subscription_id = query.data.split(';')
    if command == 'Подписка':
        client = Client.objects.get(tg_chat_id=query.message.chat_id)
        subscription = Subscription.objects.get(id=subscription_id)
        purchase = subscription.subscribe(client)
        if purchase:
            message = f'Вы оплатили подписку. Количество доступных обращений: {client.orders_left()}.\n' \
                      f'Нажмите `Заказать работу`.'
        else:
            message = 'Не удалось купить подписку.'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_MENU'
    elif command == 'Назад':
        context.bot.send_message(text='Меню', chat_id=query.message.chat_id)
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_MENU'
    elif command == 'В общее меню':
        user_name = update.effective_user.first_name
        keyboard = get_start_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f'Привет, {user_name}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU'


def handle_current_customer_order(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    if command == 'Написать фрилансеру':
        context.user_data['order_id'] = order_id
        message = 'Напишите сообщение фрилансеру в поле для ввода:'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'SENDING_MESSAGES_TO_FREELANCER'
    elif command == 'Назад':
        message = 'Ваши заказы'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'


def handle_customer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    client = Client.objects.get(tg_chat_id=query.message.chat_id)
    if not client.is_active:
        display_private_access(update, context)
        return 'MENU'
    command, payload = query.data.split(';')
    if command == 'Назад':
        message = 'Ваши заказы'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'
    _, order_id = payload.split(':')
    order = Job.objects.get(id=order_id)
    description = ''
    if order.description:
        description = f'\n\nОписание: {order.description}'
    message = f'{order.title}{description}\n\nСтатус заказа: {Job.Statuses[order.status].label}'
    keyboard = []
    if order.status == 'IN_PROGRESS' or order.status == 'DONE':
        keyboard.append([InlineKeyboardButton('Написать фрилансеру', callback_data=f'Написать фрилансеру;{order.id}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data=f'Назад;{order.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CURRENT_CUSTOMER_ORDER'


def handle_customer_orders_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    client = Client.objects.get(tg_chat_id=query.message.chat_id)
    if not client.is_active:
        display_private_access(update, context)
        return 'MENU'
    client = Client.objects.get(tg_chat_id=query.message.chat_id)
    if query.data == 'Назад':
        keyboard = get_client_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Меню:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_MENU'
    if query.data == 'Актуальные':
        status = 'IN_PROGRESS'
        orders = client.orders.exclude(status='DONE')
        message = 'Актуальные заказы:'
    else:
        status = 'DONE'
        orders = client.orders.filter(status=status)
        message = 'Выполненные заказы:'
    if not orders:
        message = 'Нет заказов'
    keyboard = get_freelancer_current_orders_keyboard(orders, status)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CUSTOMER_ORDERS'


def handle_customer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    client, _ = Client.objects.get_or_create(tg_chat_id=query.message.chat_id)
    if not client.is_active:
        display_private_access(update, context)
        return 'MENU'
    if query.data == 'Оставить заявку':
        if client.orders_left():
            message = 'Примеры названий заказов:\n' \
                      'Нужно добавить в интернет-магазин фильтр товаров по цвету\n' \
                      'Нужно выгрузить товары с сайта в Excel-таблице\nНужно загрузить 450 SKU на сайт из Excel таблицы\n\n' \
                      'Введите название вашего заказа в поле для ввода:'
            keyboard = [
                [InlineKeyboardButton('Отменить', callback_data='Отменить')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'CREATE_ORDER'
        else:
            subscriptions = Subscription.objects.all()
            keyboard = [
                [InlineKeyboardButton(
                    f'{subscription.title} за {int(subscription.price)}р. Кол-во заказов: {subscription.orders_amount}',
                    callback_data=f'Подписка;{subscription.id}')] for
                subscription in subscriptions
            ]
            keyboard.append([InlineKeyboardButton('Назад', callback_data='Назад;')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'Для создания заказа, необходимо купить подписку, выберите одну из них:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'SUBSCRIPTIONS'
    elif query.data == 'Мои заказы':
        message = 'Ваши заказы'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'
    elif query.data == 'Назад':
        user_name = update.effective_user.first_name
        keyboard = get_start_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f'Привет, {user_name}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU'


def handle_order_creation(update: Update, context: CallbackContext):
    query = update.callback_query
    client = Client.objects.get(tg_chat_id=update.message.chat_id)
    if not client.is_active:
        display_private_access(update, context)
        return 'MENU'
    if query:
        if query.data == 'Отменить':
            chat_id = query.message.chat_id
            keyboard = get_client_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'Меню:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=chat_id)
            return 'CUSTOMER_MENU'
    else:
        chat_id = update.message.chat_id
        order_title = update.message.text
        context.user_data['order_title'] = order_title
        message = 'Добавьте описание заказа:'
        context.bot.send_message(text=message, chat_id=chat_id)
        return 'DESCRIPTION_ADDING'

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from auth2.models import User, Client
from freelance_orders.keyboards import get_client_menu_keyboard, get_customer_orders_menu_keyboard, \
    get_freelancer_current_orders_keyboard
from jobs.models import Job
from products.models import Subscription


def handle_subscriptions(update: Update, context: CallbackContext):
    query = update.callback_query
    command, subscription_id = query.data.split(';')
    if command == 'Подписка':
        client = Client.objects.get(tg_chat_id=query.message.chat_id)
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.subscribe(client)
        message = f'Вы оплатили подписку. Количество доступных обращений: {subscription.orders_amount}.' \
                  f'Нажмите `Заказать работу`.'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
    keyboard = get_client_menu_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CUSTOMER_MENU'


def handle_current_customer_order(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    if command == 'Написать заказчику':
        # TODO: сделать чат с заказчиком
        pass
    elif command == 'Назад':
        message = 'Ваши заявки'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'


def handle_customer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    command, payload = query.data.split(';')
    if command == 'Назад':
        message = 'Ваши заявки'
        keyboard = get_customer_orders_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'CUSTOMER_ORDERS_MENU'
    _, order_id = payload.split(':')
    order = Job.objects.get(id=order_id)
    message = f'{order.title}\n\n{order.description}'
    keyboard = []
    if order.status == 'IN_PROGRESS' or order.status == 'DONE':
        keyboard.append([InlineKeyboardButton('Написать фрилансеру', callback_data=f'Написать фрилансеру;{order.id}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data=f'Назад;{order.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CURRENT_CUSTOMER_ORDER'


def handle_customer_orders_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    client = User.objects.get(tg_chat_id=query.message.chat_id)
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
        message = 'Нет заявок'
    keyboard = get_freelancer_current_orders_keyboard(orders, status)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CUSTOMER_ORDERS'


def handle_customer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    client = Client.objects.get(tg_chat_id=query.message.chat_id)
    if query.data == 'Оставить заявку':
        if client.orders_left():
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
            message = 'Для создания заявки, необходимо купить подписку, выберите одну из них:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'SUBSCRIPTIONS'
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

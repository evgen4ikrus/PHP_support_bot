from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from auth2.models import Freelancer
from freelance_orders.keyboards import get_freelancer_menu_keyboard, get_menu_freelancer_orders_keyboard, \
    get_freelancer_current_orders_keyboard, get_freelancer_orders_keyboard, get_start_keyboard
from jobs.models import Job


def display_private_access(update: Update, context: CallbackContext):
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
        context.bot.send_message(text=message,reply_markup=reply_markup, chat_id=chat_id)


def handle_sending_messages_to_customer(update: Update, context: CallbackContext):
    if update.message:
        text = update.message.text
        if text:
            order_id = context.user_data['order_id']
            order = Job.objects.get(id=order_id)
            message = f'Вам пришло сообщение от фрилансера, который выполняет заказ "{order.title}":\n\n' \
                      f'<b>{text}</b>\n\n' \
                      f'Чтобы ответить, найдите заказ в разделе "Мои заказы" и нажмите "Написать фрилансеру"\n' \
                      f'Нажмите `/start` для выхода в меню.'
            context.bot.send_message(text=message, chat_id=order.client.tg_chat_id, parse_mode="html")
            keyboard = [[InlineKeyboardButton('Вернуться в меню заказов', callback_data='Вернуться в меню заказов')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(text='Сообщение отправлено заказчику', reply_markup=reply_markup,
                                     chat_id=update.message.chat_id)
            return 'SENDING_MESSAGES_TO_CUSTOMER'
    query = update.callback_query
    if query:
        if query.data == 'Вернуться в меню заказов':
            keyboard = get_menu_freelancer_orders_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'Ваши заказы:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'MENU_FREELANCER_ORDERS'


def handle_current_freelancer_order(update: Update, context: CallbackContext):
    query = update.callback_query
    command, order_id = query.data.split(';')
    order = Job.objects.get(id=order_id)
    if command == 'Написать заказчику':
        context.user_data['order_id'] = order_id
        message = 'Напишите сообщение заказчику в поле для ввода:'
        context.bot.send_message(text=message, chat_id=query.message.chat_id)
        return 'SENDING_MESSAGES_TO_CUSTOMER'
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
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
    if not freelancer.is_active:
        display_private_access(update, context)
        return 'MENU'
    command, payload = query.data.split(';')
    if command == 'Назад':
        keyboard = get_menu_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Ваши заказы:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU_FREELANCER_ORDERS'
    status, order_id = payload.split(':')
    order = Job.objects.get(id=order_id)
    description = ''
    if order.description:
        description = f'\n\nОписание: {order.description}'
    message = f'{order.title}{description}\n\nСтатус заказа: {Job.Statuses[order.status].label}'
    keyboard = [
        [InlineKeyboardButton('Написать заказчику', callback_data=f'Написать заказчику;{order.id}')],
    ]
    if status == 'IN_PROGRESS':
        keyboard.append(
            [InlineKeyboardButton('Подтвердить выполнение заказа', callback_data=f'Заказ выполнен;{order.id}')])
    keyboard.append([InlineKeyboardButton('Назад', callback_data=f'Назад;{order.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
    return 'CURRENT_FREELANCER_ORDER'


def handle_menu_freelancer_orders(update: Update, context: CallbackContext):
    query = update.callback_query
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
    if not freelancer.is_active:
        display_private_access(update, context)
        return 'MENU'
    if query.data == 'Назад':
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
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
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
    if not freelancer.is_active:
        display_private_access(update, context)
        return 'MENU'
    command, order_id = query.data.split(';')
    if command == 'Взять в работу':
        order = Job.objects.get(id=order_id)
        order.freelancer = freelancer
        order.status = 'IN_PROGRESS'
        order.save()
        keyboard = get_freelancer_menu_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=f'Вы взяли в работу заказ: {order.title}', chat_id=query.message.chat_id)
        context.bot.send_message(text='Меню:', reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_MENU'
    elif command == 'Назад':
        keyboard = get_freelancer_orders_keyboard(freelancer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'


def handle_order_search(update: Update, context: CallbackContext):
    query = update.callback_query
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
    if not freelancer.is_active:
        display_private_access(update, context)
        return 'MENU'
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
        description = ''
        if order.description:
            description = f'\n\nОписание: {order.description}'
        message = f'{order.title}{description}\n\nСтатус заказа: {Job.Statuses[order.status].label}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'FREELANCER_ORDER_DESCRIPTION'
    elif command == 'Показать ещё':
        page = payload
        keyboard = get_freelancer_orders_keyboard(freelancer, page_num=page)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'


def handle_freelancer_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
    if not freelancer.is_active:
        display_private_access(update, context)
        return 'MENU'
    elif query.data == 'Найти заказ':
        freelancer = Freelancer.objects.get(tg_chat_id=query.message.chat_id)
        keyboard = get_freelancer_orders_keyboard(freelancer)
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Выберите заказ:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'ORDER_SEARCH'
    elif query.data == 'Мои заказы':
        keyboard = get_menu_freelancer_orders_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = 'Ваши заказы:'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'MENU_FREELANCER_ORDERS'
    elif query.data == 'Назад':
        user_name = update.effective_user.first_name
        keyboard = get_start_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f'Привет, {user_name}'
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id )
        return 'MENU'

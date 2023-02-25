from telegram import InlineKeyboardButton


def get_freelancer_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Найти заказ', callback_data='Найти заказ'),
            InlineKeyboardButton('Мои выполняемые заказы', callback_data='Выполняемые заказы')
        ],
    ]
    return keyboard


def get_freelancer_orders_keyboard(page):
    keyboard = [[InlineKeyboardButton(order.title, callback_data=f'Заказ;{order.id}')] for order in page.object_list]
    if page.has_next():
        keyboard.append([InlineKeyboardButton('Показать ещё', callback_data='Показать ещё')])
    keyboard.append([InlineKeyboardButton('Вернуться в меню', callback_data='Вернуться в меню')])
    return keyboard

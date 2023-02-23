from telegram import InlineKeyboardButton


def get_freelancer_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Найти заказ', callback_data='Найти заказ'),
            InlineKeyboardButton('Мои выполняемые заказы', callback_data='Выполняемые заказы')
        ],
    ]
    return keyboard


def get_freelancer_orders_keyboard():
    keyboard = [
        [InlineKeyboardButton('Заказ 1', callback_data='Заказ')],
        [InlineKeyboardButton('Заказ 2', callback_data='Заказ')],
        [InlineKeyboardButton('Показать ещё', callback_data='Показать ещё')],
        [InlineKeyboardButton('Вернуться в меню', callback_data='Вернуться в меню')],
    ]
    return keyboard

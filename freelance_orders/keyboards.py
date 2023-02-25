from telegram import InlineKeyboardButton


def get_freelancer_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Найти заказ', callback_data='Найти заказ'),
            InlineKeyboardButton('Мои заказы', callback_data='Мои заказы')
        ],
    ]
    return keyboard


def get_freelancer_orders_keyboard(page):
    keyboard = [[InlineKeyboardButton(order.title, callback_data=f'Заказ;{order.id}')] for order in page.object_list]
    if page.has_next():
        keyboard.append([InlineKeyboardButton('Показать ещё', callback_data='Показать ещё;')])
    keyboard.append([InlineKeyboardButton('Вернуться в меню', callback_data='Вернуться в меню;')])
    return keyboard


def get_start_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Я заказчик', callback_data='Заказчик'),
            InlineKeyboardButton('Я фрилансер', callback_data='Фрилансер')
        ],
    ]
    return keyboard


def get_menu_freelancer_orders_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Текущие заказы', callback_data='Текущие заказы'),
            InlineKeyboardButton('Выполненные заказы', callback_data='Выполненные заказы')
        ],
        [InlineKeyboardButton('Назад', callback_data='Назад'), ]
    ]
    return  keyboard


def get_freelancer_current_orders_keyboard(orders):
    keyboard = [[InlineKeyboardButton(order.title, callback_data=f'Заказ;{order.id}')] for order in orders]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='Назад;')])
    return keyboard

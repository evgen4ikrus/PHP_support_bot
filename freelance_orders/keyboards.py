from telegram import InlineKeyboardButton


def get_freelancer_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Найти заказ', callback_data='Найти заказ'),
            InlineKeyboardButton('Мои заказы', callback_data='Мои заказы')
        ],
    ]
    return keyboard


def get_freelancer_orders_keyboard(freelancer, page_num=1):
    page = freelancer.get_job_list(page_num)
    keyboard = [[InlineKeyboardButton(order.title, callback_data=f'Заказ;{order.id}')] for order in page.object_list]
    if page.has_next():
        next_page_num = page.next_page_number()
        keyboard.append([InlineKeyboardButton('Показать ещё', callback_data=f'Показать ещё;{next_page_num}')])
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


def get_freelancer_current_orders_keyboard(orders, status):
    keyboard = [[InlineKeyboardButton(order.title, callback_data=f'Заказ;{status}:{order.id}')] for order in orders]
    keyboard.append([InlineKeyboardButton('Назад', callback_data='Назад;:')])
    return keyboard


def get_client_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Заказать работу', callback_data='Оставить заявку'),
            InlineKeyboardButton('Мои заказы', callback_data='Мои заказы')
        ],
    ]
    return keyboard


def get_customer_orders_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton('Актуальные', callback_data='Актуальные'),
            InlineKeyboardButton('Выполненные', callback_data='Выполненные')
        ],
        [InlineKeyboardButton('Назад', callback_data='Назад'), ]
    ]
    return  keyboard

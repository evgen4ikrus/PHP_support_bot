import logging

from textwrap import dedent

from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext

from auth2.models import Client
from jobs.models import Job


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


CLIENT = 1
CLIENT_ORDER = 3


def fetch_client_menu(update: Update, context: CallbackContext) -> CLIENT:
    Client.objects.get_or_create(
        tg_chat_id=update.message.chat_id
    )

    reply_keyboard = [['Мои заявки', 'Оставить заявку']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    user = update.effective_user.first_name
    message = fr'Ты на странице подрядчика, {user}'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CLIENT


def get_client_orders(update: Update, context: CallbackContext) -> CLIENT:
    client = Client.objects.get(tg_chat_id=update.message.chat_id)
    page = client.get_my_orders()

    reply_keyboard = [
        [order.id for order in page],
        ['Меню клиента']
    ]

    if page.has_next():
        reply_keyboard = [
            [order.id for order in page],
            ['Следующие'], ['Меню клиента']
        ]
        context.user_data['number_page'] = page.next_page_number()

    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = 'Ты на странице заказов клиента'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CLIENT


def get_next_page_orders(update: Update, context: CallbackContext) -> CLIENT:
    client = Client.objects.get(tg_chat_id=update.message.chat_id)

    next_page_num = context.user_data['number_page']
    page = client.get_my_orders(next_page_num)

    reply_keyboard = [
        [order.id for order in page],
        ['Меню клиента']
    ]
    if page.has_next():
        reply_keyboard = [
            [order.id for order in page],
            ['Следующие'], ['Меню клиента']
        ]
        context.user_data['number_page'] = page.next_page_number()

    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = 'Ты на странице заказов клиента'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CLIENT


def get_order(update: Update, context: CallbackContext) -> CLIENT:
    context.user_data[CLIENT] = update.message.text
    order = Job.objects.get(id=context.user_data[CLIENT])

    message = f'''\
        ID заявки: {context.user_data[CLIENT]}
        Статус заявки: {order.status}
        Описание заявки: {order.description}
        Ваш чат ID: {order.client}
    '''
    message = dedent(message)

    reply_keyboard = [['Меню клиента']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CLIENT


def make_order(update: Update, context: CallbackContext) -> CLIENT_ORDER:
    message = '''\
        Примеры заявок:
        Здравствуйте, нужно добавить в интернет-магазин фильтр товаров по цвету

        Здравствуйте, нужно выгрузить товары с сайта в Excel-таблице

        Здравствуйте, нужно загрузить 450 SKU на сайт из Execel таблицы


        Оставьте вашу заявку
    '''
    message = dedent(message)

    update.message.reply_text(
        message
    )

    return CLIENT_ORDER


def fill_order(update: Update, context: CallbackContext) -> CLIENT:
    context.user_data[CLIENT_ORDER] = update.message.text
    title = f'Заявка {update.message.chat_id}'
    client = Client.objects.get(tg_chat_id=update.message.chat_id)
    Job.objects.get_or_create(
        client=client,
        title=title,
        description=context.user_data[CLIENT_ORDER]
    )

    reply_keyboard = [['Меню клиента']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    message = f'''\
        Ваша заявка: {context.user_data[CLIENT_ORDER]}

        Ваша заявка принята!
        В течении дня с вами свяжется менеджер.
    '''
    message = dedent(message)

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CLIENT


def client_main() -> dict:
    states = {
        CLIENT: [
            MessageHandler(Filters.regex(r'Мои заявки'), get_client_orders),
            MessageHandler(Filters.regex(r'Оставить заявку'), make_order),
            MessageHandler(Filters.regex(r'Меню клиента'), fetch_client_menu),
            MessageHandler(Filters.regex(r'\d{2}'), get_order),
            MessageHandler(Filters.regex(r'Следующие'), get_next_page_orders)
        ],
        CLIENT_ORDER: [
            MessageHandler(Filters.all, fill_order)
        ]
    }

    return states

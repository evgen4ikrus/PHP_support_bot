import logging

from textwrap import dedent

from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext, RegexHandler,  ConversationHandler

from django.core.management.base import BaseCommand
from django.conf import settings
from auth2.models import Client
from jobs.models import Job


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# константы 0, 1, 3
MENU, CL_ORDERS, FR_ORDERS, END_ORDER, GET_ORDER = range(5)


class Command(BaseCommand):
    # главное меню после вызова старт (клиент фрилансер) чекни MENU
    def start(self, update: Update, context: CallbackContext) -> MENU:
        reply_keyboard = [['Клиент', 'Фрилансер']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Привет, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return MENU

    # Меню клиента, аналогия со стартом(так же ловит его ввод и возращает константу)
    def client(self, update: Update, context: CallbackContext) -> CL_ORDERS:
        reply_keyboard = [['Мои заявки', 'Оставить заявку']]
        Client.objects.get_or_create(
            tg_chat_id=update.message.chat_id
        )
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Ты на странице подрядчика, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return CL_ORDERS

    def freelancer(self, update: Update, context: CallbackContext) -> FR_ORDERS:
        reply_keyboard = [['Мои заказы', 'Взять заказ']]
        user = update.effective_user.first_name
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = fr'Ты на странице подрядчика, {user}'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return FR_ORDERS

    def client_orders(self, update: Update, context: CallbackContext):
        client = Client.objects.get(tg_chat_id=update.message.chat_id)
        page = client.get_my_orders()
        reply_keyboard = [
            [order.id for order in page],
            ['Меню клиента']
            ]
        if page.has_next:
            reply_keyboard = [
                [order.id for order in page],
                ['Следующие'], ['Меню клиента']
            ]
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = 'Ты на странице заказов клиента'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return GET_ORDER

    def get_order(self, update: Update, context: CallbackContext) -> END_ORDER:
        context.user_data[GET_ORDER] = update.message.text
        message = f'''\
            Ваша заявка: {context.user_data[GET_ORDER]}

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

        return CL_ORDERS

    def make_order(self, update: Update, context: CallbackContext) -> END_ORDER:
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

        return END_ORDER

    def end_order(self, update: Update, context: CallbackContext):
        context.user_data[END_ORDER] = update.message.text
        reply_keyboard = [['Меню клиента']]
        title = f'Заявка {update.message.chat_id}'
        client = Client.objects.get(tg_chat_id=update.message.chat_id)
        Job.objects.get_or_create(
            client=client,
            title=title,
            description=context.user_data[END_ORDER]
        )
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )

        message = f'''\
            Ваша заявка: {context.user_data[END_ORDER]}

            Ваша заявка принята!
            В течении дня с вами свяжется менеджер.
        '''
        message = dedent(message)

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return CL_ORDERS

    def freelancer_orders(self, update: Update, context: CallbackContext):
        reply_keyboard = [[1, 2, 3], ['Меню фрилансера']]
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = 'Заказы фрилансера'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

    def take_order(self, update: Update, context: CallbackContext):
        reply_keyboard = [['Взять заказ'], ['Меню фрилансера']]
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = 'Взять заказ'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

    def cancel(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text(
            'Счастливо! Будем рады помочь вам.'
        )

        return ConversationHandler.END

    def handle(self, *args, **options):
        telegram_bot_token = settings.TELEGRAM_BOT_TOKEN

        updater = Updater(telegram_bot_token)

        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                # ловит ввод от юзера, и согласно его вводу вызывает функцию в зависимости от выбора
                MENU: [
                    RegexHandler('^(Клиент)$', self.client),
                    RegexHandler('^(Фрилансер)$', self.freelancer)
                ],
                # дальше от выбора юзера вызывается функция которая так же вызывает константу
                # либо для клиета/фрилансера по вводу которых отлавливается какую функцию вызвать
                CL_ORDERS: [
                    RegexHandler('^(Мои заявки)$', self.client_orders),
                    RegexHandler('^(Оставить заявку)$', self.make_order),
                    RegexHandler('^(Меню клиента)$', self.client)
                ],
                FR_ORDERS: [
                    RegexHandler('^(Мои заказы)$', self.freelancer_orders),
                    RegexHandler('^(Взять заказ)$', self.take_order),
                    RegexHandler('^(Меню фрилансера)$', self.freelancer)
                ],
                END_ORDER: [
                    MessageHandler(Filters.all, self.end_order)
                ],
                GET_ORDER: [
                    MessageHandler(Filters.all, self.get_order)
                ]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )

        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()

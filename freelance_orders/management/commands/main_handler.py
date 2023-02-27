import logging

from .contractor_branch import contractor_main
from .client_branch import client_main

from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext, ConversationHandler

from auth2.models import Client, Freelancer


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


MENU, CLIENT, CONTRACTOR = range(3)


def start(update: Update, context: CallbackContext) -> MENU:
    reply_keyboard = [['Клиент', 'Фрилансер']]
    user = update.effective_user.first_name
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = fr'Здравствуйте, {user}'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return MENU


def client(update: Update, context: CallbackContext) -> CLIENT:
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

    return CLIENT


def contractor(update: Update, context: CallbackContext) -> CONTRACTOR:
    contractor, _ = Freelancer.objects.get_or_create(
        tg_chat_id=update.message.chat_id
    )
    if contractor.is_active:
        reply_keyboard = [['Доступные заказы', 'Мои заказы']]
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
        message = 'Объяснение как работать с ботом и цены за работу'

        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )

        return CONTRACTOR

    user = update.effective_user.first_name
    message = fr'Ой-ей, {user}. Обратитесь к менеджеру. Вы не активны'
    update.message.reply_text(
        message
    )


def cancel(update: Update, context: CallbackContext) -> ConversationHandler.END:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Счастливо! Будем рады помочь вам.'
    )

    return ConversationHandler.END


def get_bot_handler():
    client_states = client_main()
    contractor_states = contractor_main()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [
                MessageHandler(Filters.regex(r'Клиент'), client),
                MessageHandler(Filters.regex(r'Фрилансер'), contractor)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    conv_handler.states.update(client_states)
    conv_handler.states.update(contractor_states)

    return conv_handler

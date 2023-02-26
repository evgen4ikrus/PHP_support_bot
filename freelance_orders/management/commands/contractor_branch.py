import logging

# from textwrap import dedent

from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

CONTRACTOR = 2


def freelancer(update: Update, context: CallbackContext) -> CONTRACTOR:
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

    return CONTRACTOR


def freelancer_orders(update: Update, context: CallbackContext):
    reply_keyboard = [[1, 2, 3], ['Меню фрилансера']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = 'Заказы фрилансера'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )


def contractor_main():
    states = {
        CONTRACTOR: [
            MessageHandler(Filters.regex(r'Мои заказы'), freelancer_orders),
            MessageHandler(Filters.regex(r'Меню фрилансера'), freelancer),
        ],
    }

    return states

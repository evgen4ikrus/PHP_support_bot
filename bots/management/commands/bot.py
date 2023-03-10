import telegram
from django.core.management.base import BaseCommand
from environs import Env
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater, CallbackContext, InlineQueryHandler)

from auth2.models import Freelancer, Client
from bots.client_branch_handlers import handle_customer_menu, handle_order_creation, \
    handle_customer_orders_menu, handle_customer_orders, handle_current_customer_order, handle_subscriptions, \
    handle_description_adding, handle_sending_messages_to_freelancer, handle_freelancer_message
from bots.freelancer_branch_handlers import handle_freelancer_menu, handle_order_search, \
    handle_freelancer_order_description, handle_freelancer_orders, handle_menu_freelancer_orders, \
    handle_current_freelancer_order, handle_sending_messages_to_customer, handle_customer_message
from bots.keyboards import get_freelancer_menu_keyboard, get_start_keyboard, get_client_menu_keyboard
from products.models import Subscription
from bots.bot_helpers import get_database_connection, display_private_access


def handle_users_reply(update: Update, context: CallbackContext):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(f'telegram_{chat_id}').decode('utf-8')
    states_functions = {
        'START': start,
        'MENU': handle_general_menu,
        'CUSTOMER_MENU': handle_customer_menu,
        'FREELANCER_MENU': handle_freelancer_menu,
        'ORDER_SEARCH': handle_order_search,
        'FREELANCER_ORDER_DESCRIPTION': handle_freelancer_order_description,
        'FREELANCER_ORDERS': handle_freelancer_orders,
        'MENU_FREELANCER_ORDERS': handle_menu_freelancer_orders,
        'CURRENT_FREELANCER_ORDER': handle_current_freelancer_order,
        'SENDING_MESSAGES_TO_CUSTOMER': handle_sending_messages_to_customer,
        'CREATE_ORDER': handle_order_creation,
        'DESCRIPTION_ADDING': handle_description_adding,
        'CUSTOMER_ORDERS_MENU': handle_customer_orders_menu,
        'CUSTOMER_ORDERS': handle_customer_orders,
        'CURRENT_CUSTOMER_ORDER': handle_current_customer_order,
        'SUBSCRIPTIONS': handle_subscriptions,
        'HANDLE_USERS_REPLY': handle_users_reply,
        'SENDING_MESSAGES_TO_FREELANCER': handle_sending_messages_to_freelancer,
        'HANDLE_CUSTOMER_MESSAGE': handle_customer_message,
        'HANDLE_FREELANCER_MESSAGE': handle_freelancer_message,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(f'telegram_{chat_id}', next_state)


def handle_general_menu(update: Update, context: CallbackContext):
    user_name = update.effective_user.first_name
    query = update.callback_query
    if query.data == '????????????????':
        client, _ = Client.objects.get_or_create(tg_chat_id=query.message.chat_id)
        if not client.is_active:
            display_private_access(update, context)
            return 'MENU'
        if client.orders_left():
            keyboard = get_client_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = '????????:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'CUSTOMER_MENU'
        else:
            subscriptions = Subscription.objects.all()
            keyboard = [
                [InlineKeyboardButton(
                    f'{subscription.title} ???? {int(subscription.price)}??. ??????-???? ??????????????: {subscription.orders_amount}',
                    callback_data=f'????????????????;{subscription.id}')] for
                subscription in subscriptions
            ]
            keyboard.append([InlineKeyboardButton('??????????', callback_data='?? ?????????? ????????;')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = '?????? ???????????????? ????????????, ???????????????????? ???????????? ????????????????, ???????????????? ???????? ???? ??????:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'SUBSCRIPTIONS'
    elif query.data == '??????????????????':
        freelancer, _ = Freelancer.objects.get_or_create(tg_chat_id=query.message.chat_id)
        if not freelancer.is_active:
            display_private_access(update, context)
            return 'MENU'
        if freelancer.is_active_freelancer:
            keyboard = get_freelancer_menu_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = '????????:'
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'FREELANCER_MENU'
        message = f'{user_name}, ?? ?????????????????? 10 ?????????? ?? ???????? ???????????????? ?????? ????????????????.'
        keyboard = [[InlineKeyboardButton('??????????', callback_data='??????????')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
        return 'START'


def start(update: Update, context: CallbackContext):
    query = update.callback_query
    user_name = update.effective_user.first_name
    keyboard = get_start_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f'????????????, {user_name}'
    if query:
        if query.data == '??????????':
            context.bot.send_message(text=message, reply_markup=reply_markup, chat_id=query.message.chat_id)
            return 'MENU'
    update.message.reply_text(text=message, reply_markup=reply_markup)
    return 'MENU'


class Command(BaseCommand):
    env = Env()
    env.read_env()
    tg_token = env('TELEGRAM_BOT_TOKEN')
    tg_bot = telegram.Bot(token=tg_token)
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(InlineQueryHandler(handle_customer_message))

    updater.start_polling()
    updater.idle()

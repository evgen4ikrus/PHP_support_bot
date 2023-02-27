import logging

from textwrap import dedent

from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters
from telegram.ext import CallbackContext
from django.utils import timezone

from auth2.models import Client, Freelancer
from jobs.models import Job


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

CONTRACTOR = 2
TAKE_JOB = 4


def freelancer(update: Update, context: CallbackContext) -> CONTRACTOR:
    reply_keyboard = [['Доступные заказы', 'Мои заказы']]
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


def get_job(update: Update, context: CallbackContext) -> CONTRACTOR:
    contractor = Freelancer.objects.get(tg_chat_id=update.message.chat_id)
    jobs = contractor.get_job_list()
    reply_keyboard = [[job.id for job in jobs], ['Меню фрилансера']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = 'Заказы фрилансера'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CONTRACTOR


def show_contractor_jobs(update: Update, context: CallbackContext) -> CONTRACTOR:
    contractor = Freelancer.objects.get(tg_chat_id=update.message.chat_id)
    jobs = Job.objects.filter(freelancer=contractor)
    reply_keyboard = [[job.id for job in jobs], ['Меню фрилансера']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )
    message = 'Заказы фрилансера'

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CONTRACTOR


def view_job(update: Update, context: CallbackContext) -> CONTRACTOR:
    context.user_data[CONTRACTOR] = update.message.text
    context.user_data['id_job'] = context.user_data[CONTRACTOR]
    order = Job.objects.get(id=context.user_data[CONTRACTOR])

    message = f'''\
        ID заявки: {context.user_data[CONTRACTOR]}
        Статус заявки: {order.status}
        Описание заявки: {order.description}
        Клиент: {order.client}
    '''
    message = dedent(message)

    reply_keyboard = [['Взять заявку'], ['Доступные заказы']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CONTRACTOR


def take_job(update: Update, context: CallbackContext) -> CONTRACTOR:
    job_id = context.user_data['id_job']

    message = f'''\
        ID заявки: {job_id}

        Введите предпологаемое количество дней для выполнения
    '''
    message = dedent(message)

    update.message.reply_text(
        message
    )

    return TAKE_JOB


def save_job(update: Update, context: CallbackContext) -> CONTRACTOR:
    job_id = context.user_data['id_job']
    job = Job.objects.get(id=job_id)
    contractor = Freelancer.objects.get(tg_chat_id=update.message.chat_id)
    deadline = timezone.now() + timezone.timedelta(days=int(update.message.text))
    job.take(contractor, deadline)

    message = f'''\
        ID заявки клиента: {job_id}
        Вы взяли заявку
    '''
    message = dedent(message)

    reply_keyboard = [['Доступные заказы']]
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

    return CONTRACTOR


def contractor_main():
    states = {
        CONTRACTOR: [
            MessageHandler(Filters.regex(r'Меню фрилансера'), freelancer),
            MessageHandler(Filters.regex(r'Доступные заказы'), get_job),
            MessageHandler(Filters.regex(r'Мои заказы'), show_contractor_jobs),
            MessageHandler(Filters.regex(r'\d+'), view_job),
            MessageHandler(Filters.regex(r'Взять заявку'), take_job),
        ],
        TAKE_JOB: [
            MessageHandler(Filters.all, save_job)
        ]
    }

    return states

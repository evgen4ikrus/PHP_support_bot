# PHP_support_bot

## Установка и запуск
* Скачайте код и перейдите в папку проекта
* Создайте виртуальное окружение:
```commandline
python3 -m venv venv
```
* Активируйте виртуальное окружение:
```commandline
. venv/bin/activate
```
* Установите зависимости:
```
python3 -m pip install -r requirements.txt
```
* Сделайте копию файла env.example и назовите его .env
```
cp env.example .env
```
* Задайте значения переменным в файле .env:
```
TELEGRAM_BOT_TOKEN - токен Вашего telegram бота
DJANGO_SETTINGS_MODULE - модуль настроек, по-умолчанию 'PHP_support_bot.settings.dev'
SECRET_KEY - секретный ключ джанго
ALLOWED_HOSTS - список разрешенных хостов
REDIS_DATABASE_PASSWORD
REDIS_DATABASE_HOST
REDIS_DATABASE_PORT
```
* Примените миграции БД:
```commandline
python3 manage.py migrate
```
* Запустите сайт:
```commandline
python3 manage.py runserver
```
* Перейдите по [ссылке](http://127.0.0.1:8000/admin/), если всё выполнено верно, то откроется админка сайта.
* Запустите бота:
```commandline
python3 manage.py bot
```

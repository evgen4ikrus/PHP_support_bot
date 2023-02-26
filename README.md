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
* Создайте файл .env в корневой папке проекта, и запишите в него переменные окружения в формате `КЛЮЧ=ЗНАЧЕНИЕ`
(отмеченные звездочкой определять необязательно, у них есть дефолдные значения):
```
TELEGRAM_BOT_TOKEN - токен Вашего telegram бота
*SECRET_KEY - секретный ключ джанго # по умолчанию `12345`
*DEBUG - дебаг-режим #по умолчанию True
*ALLOWED_HOSTS - список разрешенных хостов # по умолчанию `127.0.0.1`
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

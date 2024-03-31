import os

VERSION = '1.0.0'

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

AUTH_SECRET = os.environ.get('AUTH_SECRET')

INSERT_ACCESS_KEY = os.environ.get('INSERT_ACCESS_KEY')

ORDERS_NOTIFICATION_CHATS = os.environ.get('ORDERS_NOTIFICATION_CHATS').split(';')
ORDERS_NOTIFICATION_BOT_TOKEN = os.environ.get('ORDERS_NOTIFICATION_BOT_TOKEN')

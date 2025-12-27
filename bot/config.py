import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://codepass.pythonanywhere.com/')
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 8080
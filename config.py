import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'diary')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'diary')

# Simple password (1-4 digits)
PASSWORD = os.getenv('DIARY_PASSWORD', '1234')

# AI API configuration
AI_API_URL = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')

# Telegram configuration
TELEGRAM_BOT_KEY = os.getenv('TELEGRAM_BOT_KEY', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

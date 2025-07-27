import requests
import config


def send_message(text):
    if not config.TELEGRAM_BOT_KEY or not config.TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_KEY}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=payload, timeout=30)
    except Exception:
        pass

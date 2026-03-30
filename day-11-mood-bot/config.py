import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

# Список прокси в порядке попыток
PROXIES = [
    ("socks5://127.0.0.1:10808", "Blacktemple SOCKS5"),
    ("http://127.0.0.1:2080", "VPN HTTP 2080"),
    ("http://127.0.0.1:9080", "HTTP 9080"),
    ("socks5://127.0.0.1:1080", "SOCKS5 1080"),
    ("socks5://127.0.0.1:9050", "Tor SOCKS5"),
    ("http://127.0.0.1:3128", "HTTP 3128"),
    (None, "Прямое подключение (без прокси)"),
]

# Попробуем подключиться через разные прокси

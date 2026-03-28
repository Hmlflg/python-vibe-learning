from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard():
    """Главное меню"""
    kb = [
        [KeyboardButton(text="➕ Добавить расход")],
        [KeyboardButton(text="📋 Все расходы")],
        [KeyboardButton(text="📊 Статистика")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

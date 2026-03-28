from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard():
    """Главное меню"""
    kb = [
        [KeyboardButton(text="➕ Добавить расход")],
        [KeyboardButton(text="📋 Все расходы")],
        [KeyboardButton(text="📊 Статистика")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard():
    """Клавиатура для процесса добавления расхода"""
    kb = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

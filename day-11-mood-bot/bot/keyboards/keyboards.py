from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard():
    """Главное меню бота"""
    kb = [
        [KeyboardButton(text="➕ Записать настроение")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="📅 История")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_mood_keyboard():
    """Клавиатура выбора настроения (5 вариантов)"""
    kb = [
        [KeyboardButton(text="😊 Отличное")],
        [KeyboardButton(text="🙂 Хорошее")],
        [KeyboardButton(text="😐 Нормальное")],
        [KeyboardButton(text="😔 Плохое")],
        [KeyboardButton(text="😢 Ужасное")],
        [KeyboardButton(text="❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    """Клавиатура выбора настроения (эмодзи)"""
    kb = [
        [
            KeyboardButton(text="😊"),
            KeyboardButton(text="🥰"),
            KeyboardButton(text="😌"),
            KeyboardButton(text="⚡"),
        ],
        [
            KeyboardButton(text="😔"),
            KeyboardButton(text="😟"),
            KeyboardButton(text="😠"),
            KeyboardButton(text="😴"),
        ],
        [
            KeyboardButton(text="🔥"),
            KeyboardButton(text="🙏"),
            KeyboardButton(text="🏆"),
            KeyboardButton(text="😤"),
        ],
        [KeyboardButton(text="❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_cancel_keyboard():
    """Простая клавиатура отмены"""
    kb = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

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
        [KeyboardButton(text="📅 История"), KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="🗓 Календарь")],
        [KeyboardButton(text="❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выбери действие..."
    )


def get_mood_inline_keyboard():
    """Inline-клавиатура выбора настроения (5 вариантов)"""
    kb = [
        [InlineKeyboardButton(text="😊 Отличное", callback_data="mood_😊")],
        [InlineKeyboardButton(text="🙂 Хорошее", callback_data="mood_🙂")],
        [InlineKeyboardButton(text="😐 Нормальное", callback_data="mood_😐")],
        [InlineKeyboardButton(text="😔 Плохое", callback_data="mood_😔")],
        [InlineKeyboardButton(text="😢 Ужасное", callback_data="mood_😢")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="cancel_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)




def get_confirm_keyboard():
    """Клавиатура подтверждения сохранения"""
    kb = [
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="confirm_save"),
            InlineKeyboardButton(text="✏️ Изменить", callback_data="confirm_edit"),
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_cancel_inline_keyboard():
    """Inline-клавиатура отмены"""
    kb = [[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_stats_period_keyboard(current_period: str = "all"):
    """Inline-клавиатура выбора периода для статистики"""
    kb = [
        [
            InlineKeyboardButton(
                text="📅 Неделя" + (" ✅" if current_period == "week" else ""),
                callback_data="stats_period_week",
            ),
            InlineKeyboardButton(
                text="📆 Месяц" + (" ✅" if current_period == "month" else ""),
                callback_data="stats_period_month",
            ),
            InlineKeyboardButton(
                text="📊 Всё" + (" ✅" if current_period == "all" else ""),
                callback_data="stats_period_all",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

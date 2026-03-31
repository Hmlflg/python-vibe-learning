from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_main_keyboard():
    """Главное меню бота"""
    kb = [
        [KeyboardButton(text="➕ Записать состояние")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="🗓 Календарь")],
        [KeyboardButton(text="❓ Помощь")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выбери действие..."
    )


def get_mood_inline_keyboard():
    """Inline-клавиатура выбора состояния (5 вариантов)"""
    kb = [
        [InlineKeyboardButton(text="😊 Отлично", callback_data="mood_😊")],
        [InlineKeyboardButton(text="🙂 Хорошо", callback_data="mood_🙂")],
        [InlineKeyboardButton(text="😐 Нормально", callback_data="mood_😐")],
        [InlineKeyboardButton(text="😔 Плохо", callback_data="mood_😔")],
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


def get_comment_action_keyboard():
    """Inline-клавиатура для шага комментария."""
    kb = [
        [InlineKeyboardButton(text="➡️ Пропустить", callback_data="skip_comment")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_stats_period_keyboard(current_period: str = "all"):
    """Inline-клавиатура выбора периода для статистики"""
    kb = [
        [
            InlineKeyboardButton(
                text="📍 Сегодня" + (" ✅" if current_period == "day" else ""),
                callback_data="stats_period_day",
            ),
            InlineKeyboardButton(
                text="📅 Неделя" + (" ✅" if current_period == "week" else ""),
                callback_data="stats_period_week",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📆 Месяц" + (" ✅" if current_period == "month" else ""),
                callback_data="stats_period_month",
            ),
            InlineKeyboardButton(
                text="📊 Всё время" + (" ✅" if current_period == "all" else ""),
                callback_data="stats_period_all",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_calendar_navigation_keyboard(year: int, month: int):
    """Inline-клавиатура для переключения месяцев календаря."""
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    kb = [
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"calendar_month_{prev_year}_{prev_month:02d}",
            ),
            InlineKeyboardButton(
                text="Сегодня",
                callback_data="calendar_month_current",
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"calendar_month_{next_year}_{next_month:02d}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

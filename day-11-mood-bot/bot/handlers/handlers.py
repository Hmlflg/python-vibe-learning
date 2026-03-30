from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.keyboards.keyboards import (
    get_cancel_inline_keyboard,
    get_confirm_keyboard,
    get_main_keyboard,
    get_mood_inline_keyboard,
    get_stats_period_keyboard,
)
from bot.states import MoodStates, StatsStates
from database.repository import add_mood_entry, get_mood_statistics, get_user_entries
from database.session import get_db

router = Router()

MOOD_NAMES = {
    "😊": "Отличное",
    "🙂": "Хорошее",
    "😐": "Нормальное",
    "😔": "Плохое",
    "😢": "Ужасное",
}


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я <b>Mood</b> — твой трекер настроения.\n\n"
        "Здесь ты можешь регулярно отмечать, как себя чувствуешь, "
        "и потом смотреть свою историю и статистику.\n\n"
        "Давай начнём?",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "➕ Записать настроение")
async def start_mood_entry(message: types.Message, state: FSMContext):
    """Начинает процесс записи настроения"""
    await message.answer(
        "Как ты сейчас себя чувствуешь?\nВыбери вариант:",
        reply_markup=get_mood_inline_keyboard(),
    )
    await state.set_state(MoodStates.waiting_for_mood)


@router.callback_query(F.data.startswith("mood_"))
async def process_mood_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор настроения (inline)"""
    if not callback.data:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    mood_emoji = callback.data.split("_")[1]

    await state.update_data(mood_emoji=mood_emoji)
    if callback.message:
        await callback.message.edit_text(  # type: ignore[union-attr]
            f"🎭 Выбрано настроение: <b>{MOOD_NAMES.get(mood_emoji, mood_emoji)}</b>\n\n"
            "📝 Напиши комментарий к своему настроению\n"
            "<i>(или отправь '-' чтобы пропустить)</i>",
            reply_markup=get_cancel_inline_keyboard(),
        )
    await state.set_state(MoodStates.waiting_for_comment)
    await callback.answer()



@router.message(MoodStates.waiting_for_comment, F.text)
async def process_comment(message: types.Message, state: FSMContext):
    """Сохраняет комментарий и показывает предпросмотр"""
    comment = message.text.strip() if message.text and message.text != "-" else None

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")

    if not mood_emoji:
        await message.answer("❌ Ошибка: данные потеряны. Начни заново.")
        await state.clear()
        return

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Настроение: {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
        f"📝 Комментарий: {comment if comment else '—'}\n\n"
        "Всё верно?"
    )

    await state.update_data(comment=comment)
    await state.set_state(MoodStates.waiting_for_confirm)

    await message.answer(preview_text, reply_markup=get_confirm_keyboard())


@router.callback_query(F.data == "confirm_save")
async def confirm_save_callback(callback: CallbackQuery, state: FSMContext):
    """Сохраняет запись в базу данных"""
    if not callback.from_user:
        await callback.answer("❌ Ошибка пользователя", show_alert=True)
        await state.clear()
        return

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")
    comment = data.get("comment")

    if not mood_emoji:
        await callback.answer("❌ Ошибка: данные потеряны", show_alert=True)
        await state.clear()
        return

    user_id = callback.from_user.id

    db = next(get_db())
    entry = add_mood_entry(
        db=db,
        user_id=user_id,
        mood_emoji=mood_emoji,
        comment=comment,
    )

    await state.clear()

    await callback.message.answer(  # type: ignore[union-attr]
        f"✅ <b>Настроение сохранено!</b>\n\n"
        f"🎭 {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
        f"📝 Комментарий: {comment if comment else '—'}\n"
        f"🆔 Запись # {entry.id}",
        reply_markup=get_main_keyboard(),
    )
    if callback.message:
        await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "confirm_edit")
async def confirm_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Возвращает к редактированию комментария"""
    await state.set_state(MoodStates.waiting_for_comment)
    if callback.message:
        await callback.message.edit_text(  # type: ignore[union-attr]
            "✏️ Напиши новый комментарий:",
            reply_markup=get_cancel_inline_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "confirm_cancel")
async def confirm_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отменяет создание записи"""
    await state.clear()
    if callback.message:
        await callback.message.answer(  # type: ignore[union-attr]
            "❌ Создание записи отменено",
            reply_markup=get_main_keyboard(),
        )
        await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отменяет текущее действие"""
    await state.clear()
    if callback.message:
        await callback.message.answer(  # type: ignore[union-attr]
            "❌ Действие отменено",
            reply_markup=get_main_keyboard(),
        )
        await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer()


@router.callback_query(F.data == "cancel_to_menu")
async def cancel_to_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню при выборе настроения"""
    await state.clear()
    if callback.message:
        await callback.message.answer(  # type: ignore[union-attr]
            "📍 Главное меню:",
            reply_markup=get_main_keyboard(),
        )
        await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer()


@router.message(F.text == "📅 История")
async def show_history(message: types.Message):
    """Показывает историю последних записей настроения"""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    db = next(get_db())
    entries = get_user_entries(db, user_id=message.from_user.id, limit=15)

    if not entries:
        await message.answer("📭 Пока нет записей настроения.")
        return

    text = "📅 <b>Твоя история настроения</b>\n\n"

    for entry in entries:
        text += f"{entry.timestamp.strftime('%d.%m %H:%M')}  {entry.mood_emoji}  "

        comment = str(entry.comment).strip() if entry.comment is not None else ""
        if comment:
            text += f"— {comment}\n"
        else:
            text += "\n"

    await message.answer(text, reply_markup=get_main_keyboard())


@router.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message, state: FSMContext):
    """Показывает статистику настроения"""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    await state.set_state(StatsStates.viewing_stats)
    await state.update_data(period="all")
    await show_stats_message(message, state, "all")


async def show_stats_message(message: types.Message, state: FSMContext, period: str):
    """Формирует и отправляет сообщение со статистикой"""
    if not message.from_user:
        return

    db = next(get_db())
    stats = get_mood_statistics(db, user_id=message.from_user.id, period=period)
    await state.update_data(period=period)

    period_names = {
        "week": "за неделю",
        "month": "за месяц",
        "all": "за всё время",
    }

    if stats["total"] == 0:
        await message.answer(
            f"📭 Пока нет данных {period_names.get(period, 'за этот период')}.\n"
            "Добавь несколько записей настроения.",
            reply_markup=get_main_keyboard(),
        )
        return

    # Текстовая гистограмма
    def make_bar(percent: int, max_width: int = 10) -> str:
        filled = int((percent / 100) * max_width)
        return "█" * filled + "░" * (max_width - filled)

    text = f"📊 <b>Статистика {period_names.get(period, '')}</b>\n\n"
    text += f"📌 Всего записей: <b>{stats['total']}</b>\n"
    text += f"📈 В день: <b>{stats['avg_per_day']}</b>\n"
    
    # Серия дней
    streak = stats.get("streak", 0)
    if streak > 0:
        if streak >= 7:
            streak_emoji = "🔥"
        elif streak >= 3:
            streak_emoji = "✨"
        else:
            streak_emoji = "📝"
        text += f"{streak_emoji} Серия: <b>{streak} дн.</b>\n"
    
    text += "\n"

    # Сортировка настроений по количеству
    sorted_moods = sorted(
        stats["moods"].items(), key=lambda x: x[1]["count"], reverse=True
    )

    text += "🎭 Настроения:\n"
    for emoji, data in sorted_moods:
        count = data["count"]
        percent = data["percent"]
        bar = make_bar(percent)
        text += f"{emoji} {bar} <b>{count}</b> ({percent}%)\n"

    # Добавляем инлайн-клавиатуру с периодами
    await message.answer(
        text,
        reply_markup=get_stats_period_keyboard(period),
    )


@router.callback_query(F.data.startswith("stats_period_"))
async def process_stats_period_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор периода статистики"""
    if not callback.data or not callback.message:
        await callback.answer()
        return

    period = callback.data.replace("stats_period_", "")
    await state.update_data(period=period)
    
    # Отправляем новое сообщение со статистикой
    await show_stats_message(callback.message, state, period)  # type: ignore[arg-type]
    await callback.message.delete()  # type: ignore[union-attr]
    await callback.answer()


@router.message(F.text == "🗓 Календарь")
async def show_calendar(message: types.Message):
    """Показывает красивый календарь настроения за текущий месяц"""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    import calendar
    from datetime import datetime

    db = next(get_db())
    entries = get_user_entries(db, user_id=message.from_user.id, limit=1000)

    # Создаём словарь: дата → эмодзи
    mood_by_day = {}
    for entry in entries:
        day_key = entry.timestamp.strftime("%Y-%m-%d")
        mood_by_day[day_key] = entry.mood_emoji

    now = datetime.now()
    year, month = now.year, now.month
    today = now.strftime("%Y-%m-%d")

    cal = calendar.monthcalendar(year, month)

    text = f"🗓 <b>Календарь настроения — {now.strftime('%B %Y')}</b>\n\n"

    for week in cal:
        week_line = ""
        for day_num in week:
            if day_num == 0:
                week_line += "   "
                continue

            date_str = f"{year}-{month:02d}-{day_num:02d}"
            emoji = mood_by_day.get(date_str, "⚪")

            # Цветовая индикация
            if emoji in ["😊", "🙂"]:
                color_emoji = "🟢"
            elif emoji == "😐":
                color_emoji = "🟡"
            elif emoji in ["😔", "😢"]:
                color_emoji = "🔴"
            else:
                color_emoji = "⚪"

            # Выделяем сегодняшний день
            if date_str == today:
                week_line += f"**{day_num:2d}**{emoji} "
            else:
                week_line += f"{day_num:2d}{emoji} "

        text += week_line.rstrip() + "\n"

    text += "\n🟢 Хорошее · 🟡 Нормальное · 🔴 Плохое · ⚪ Нет данных"

    await message.answer(text, reply_markup=get_main_keyboard())


@router.message(F.text.in_(["❓ Помощь", "/menu"]))
async def show_menu(message: types.Message):
    """Возвращает пользователя в главное меню"""
    await message.answer("📍 Главное меню:", reply_markup=get_main_keyboard())


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Отмена любого действия"""
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=get_main_keyboard())

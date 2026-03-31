from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.keyboards.keyboards import (
    get_calendar_navigation_keyboard,
    get_cancel_inline_keyboard,
    get_comment_action_keyboard,
    get_confirm_keyboard,
    get_main_keyboard,
    get_mood_inline_keyboard,
    get_stats_period_keyboard,
)
from bot.states import MoodStates, StatsStates
from database.repository import (
    add_mood_entry,
    get_entries_for_month,
    get_latest_entry_for_day,
    get_mood_statistics,
    get_user_entries,
    update_mood_entry,
    utc_now,
)
from database.session import create_session
from sqlalchemy.exc import SQLAlchemyError

router = Router()

MOOD_NAMES = {
    "😊": "Отлично",
    "🙂": "Хорошо",
    "😐": "Нормально",
    "😔": "Плохо",
    "😢": "Ужасно",
}


def format_month_title(year: int, month: int) -> str:
    month_names = [
        "январь",
        "февраль",
        "март",
        "апрель",
        "май",
        "июнь",
        "июль",
        "август",
        "сентябрь",
        "октябрь",
        "ноябрь",
        "декабрь",
    ]
    return f"{month_names[month - 1].capitalize()} {year}"


def build_calendar_text(entries, year: int, month: int) -> str:
    """Строит календарь состояний за текущий месяц."""
    import calendar

    mood_by_day = {}
    for entry in entries:
        day_key = entry.timestamp.strftime("%Y-%m-%d")
        mood_by_day[day_key] = entry.mood_emoji

    now = utc_now()
    today = now.strftime("%Y-%m-%d")
    cal = calendar.monthcalendar(year, month)

    text = f"🗓 <b>Календарь состояний — {format_month_title(year, month)}</b>\n\n"
    text += "<pre>Пн Вт Ср Чт Пт Сб Вс\n"

    for week in cal:
        week_cells = []
        for day_num in week:
            if day_num == 0:
                week_cells.append("   ")
                continue

            date_str = f"{year}-{month:02d}-{day_num:02d}"
            emoji = mood_by_day.get(date_str, "⚪")
            is_today = date_str == today and year == now.year and month == now.month
            day_label = f"[{day_num:02d}]" if is_today else f" {day_num:02d}"
            week_cells.append(f"{day_label}{emoji}")

        text += " ".join(week_cells).rstrip() + "\n"

    text += "</pre>\nСегодня выделен квадратными скобками.\n"
    text += "⚪ Нет данных · 😢/😔 тяжело · 😐 нейтрально · 🙂/😊 хорошо"
    return text


def build_help_text() -> str:
    return (
        "❓ <b>Что умеет бот</b>\n\n"
        "➕ <b>Записать состояние</b> — создать новую запись.\n"
        "📊 <b>Моя статистика</b> — сводка за сегодня, неделю, месяц и всё время.\n"
        "🗓 <b>Календарь</b> — месячный обзор с переключением по месяцам.\n\n"
        "Во время ввода комментария можно нажать <b>Пропустить</b>, если текст не нужен."
    )


def get_accessible_message(
    message: Message | types.InaccessibleMessage | None,
) -> Message | None:
    """Возвращает обычное сообщение, если оно доступно для редактирования/ответа."""
    return message if isinstance(message, Message) else None


def format_entry_summary(entry) -> str:
    """Коротко форматирует запись состояния."""
    if entry is None:
        return "—"

    comment = entry.comment.strip() if entry.comment else "без комментария"
    return (
        f"{entry.timestamp.strftime('%H:%M')} · "
        f"{MOOD_NAMES.get(entry.mood_emoji, entry.mood_emoji)} {entry.mood_emoji}"
        f" · {comment}"
    )


def build_stats_insight(stats: dict, period: str) -> str:
    """Строит короткий вывод по статистике периода."""
    dominant = stats.get("dominant_mood")
    if not dominant:
        return "Пока рано делать выводы."

    mood_label = MOOD_NAMES.get(dominant["emoji"]) or str(dominant["emoji"])
    mood_name = mood_label.lower()

    if period == "day":
        return f"Сегодня чаще всего состояние было: {mood_name}."
    if period == "week":
        return f"За неделю чаще всего у тебя было состояние: {mood_name}."
    if period == "month":
        return f"За месяц чаще всего повторялось состояние: {mood_name}."
    return f"За всё время чаще всего встречалось состояние: {mood_name}."


def build_stats_text(stats: dict, period: str) -> str:
    """Формирует удобный текст статистики."""
    period_names = {
        "day": "за сегодня",
        "week": "за неделю",
        "month": "за месяц",
        "all": "за всё время",
    }

    if stats["total"] == 0:
        return (
            f"📭 Пока нет данных {period_names.get(period, 'за этот период')}.\n"
            "Добавь первую запись состояния."
        )

    def make_bar(percent: int, max_width: int = 10) -> str:
        filled = int((percent / 100) * max_width)
        return "█" * filled + "░" * (max_width - filled)

    text = f"📊 <b>Статистика {period_names.get(period, '')}</b>\n\n"
    dominant = stats.get("dominant_mood")
    latest_entry = stats.get("latest_entry")

    if period == "day":
        text += f"📌 Записей сегодня: <b>{stats['total']}</b>\n"
        text += f"🕒 Последняя запись: <b>{format_entry_summary(latest_entry)}</b>\n"
    else:
        text += f"📌 Всего записей: <b>{stats['total']}</b>\n"
        text += f"📈 Среднее в день: <b>{stats['avg_per_day']}</b>\n"
        text += f"🗓 Активных дней: <b>{stats.get('active_days', 0)}</b>\n"

        streak = stats.get("streak", 0)
        if streak > 0:
            text += f"🔥 Серия записей: <b>{streak} дн.</b>\n"

        if period == "all":
            text += f"🧭 Дней с первой записи: <b>{stats.get('tracking_days', 0)}</b>\n"

    if dominant:
        text += (
            f"🏆 Чаще всего: <b>{MOOD_NAMES.get(dominant['emoji'], dominant['emoji'])} "
            f"{dominant['emoji']}</b> ({dominant['count']} раз, {dominant['percent']}%)\n"
        )

    if period in {"month", "all"}:
        best_day = stats.get("best_day")
        worst_day = stats.get("worst_day")
        if best_day:
            text += f"🌤 Лучший день: <b>{best_day['date'].strftime('%d.%m')}</b>\n"
        if worst_day:
            text += f"🌧 Самый тяжёлый день: <b>{worst_day['date'].strftime('%d.%m')}</b>\n"

    text += "\n🎭 <b>Распределение состояний</b>\n"
    sorted_moods = sorted(
        stats["moods"].items(), key=lambda x: x[1]["count"], reverse=True
    )
    for emoji, data in sorted_moods:
        text += (
            f"{emoji} {make_bar(data['percent'])} <b>{data['count']}</b> ({data['percent']}%)\n"
        )

    text += f"\n💡 <b>Итог:</b> {build_stats_insight(stats, period)}"
    return text


async def show_calendar_message(
    message: types.Message, user_id: int, year: int, month: int
):
    with create_session() as db:
        entries = get_entries_for_month(db, user_id=user_id, year=year, month=month)

    text = build_calendar_text(entries, year, month)
    await message.answer(
        text,
        reply_markup=get_calendar_navigation_keyboard(year, month),
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я <b>Mood</b> — твой трекер состояний.\n\n"
        "Здесь ты можешь регулярно отмечать, как себя чувствуешь, "
        "и потом смотреть свою историю и статистику.\n\n"
        "Давай начнём?",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "➕ Записать состояние")
async def start_mood_entry(message: types.Message, state: FSMContext):
    """Начинает процесс записи состояния."""
    await state.clear()
    await message.answer(
        "Как ты сейчас себя чувствуешь?\nВыбери вариант: Отлично, хорошо, нормально, плохо или ужасно.",
        reply_markup=get_mood_inline_keyboard(),
    )
    await state.set_state(MoodStates.waiting_for_mood)


@router.callback_query(F.data.startswith("mood_"))
async def process_mood_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор состояния через inline-кнопки."""
    if not callback.data:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    mood_emoji = callback.data.split("_")[1]
    message = get_accessible_message(callback.message)

    await state.update_data(mood_emoji=mood_emoji)
    if message:
        await message.edit_text(
            f"🎭 Выбрано состояние: <b>{MOOD_NAMES.get(mood_emoji, mood_emoji)}</b>\n\n"
            "📝 Напиши комментарий к своему состоянию\n"
            "<i>Или нажми кнопку «Пропустить» ниже.</i>",
            reply_markup=get_comment_action_keyboard(),
        )
    await state.set_state(MoodStates.waiting_for_comment)
    await callback.answer()


@router.message(MoodStates.waiting_for_comment, F.text)
async def process_comment(message: types.Message, state: FSMContext):
    """Сохраняет комментарий и показывает предпросмотр"""
    comment = message.text.strip() if message.text else None

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")

    if not mood_emoji:
        await message.answer("❌ Ошибка: данные потеряны. Начни заново.")
        await state.clear()
        return

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Состояние: {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
        f"📝 Комментарий: {comment if comment else '—'}\n\n"
        "Всё верно?"
    )
    if data.get("editing_entry_id"):
        preview_text = (
            "📋 <b>Проверь изменения перед сохранением:</b>\n\n"
            f"🎭 Состояние: {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
            f"📝 Комментарий: {comment if comment else '—'}\n\n"
            "Обновить запись?"
        )

    await state.update_data(comment=comment)
    await state.set_state(MoodStates.waiting_for_confirm)

    await message.answer(preview_text, reply_markup=get_confirm_keyboard())


@router.callback_query(F.data == "skip_comment")
async def skip_comment_callback(callback: CallbackQuery, state: FSMContext):
    """Пропускает ввод комментария и показывает предпросмотр."""
    message = get_accessible_message(callback.message)
    if not message:
        await callback.answer()
        return

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")

    if not mood_emoji:
        await callback.answer("❌ Ошибка: данные потеряны", show_alert=True)
        await state.clear()
        return

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Состояние: {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
        "📝 Комментарий: —\n\n"
        "Всё верно?"
    )
    if data.get("editing_entry_id"):
        preview_text = (
            "📋 <b>Проверь изменения перед сохранением:</b>\n\n"
            f"🎭 Состояние: {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
            "📝 Комментарий: —\n\n"
            "Обновить запись?"
        )

    await state.update_data(comment=None)
    await state.set_state(MoodStates.waiting_for_confirm)
    await message.edit_text(
        preview_text,
        reply_markup=get_confirm_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_save")
async def confirm_save_callback(callback: CallbackQuery, state: FSMContext):
    """Сохраняет запись в базу данных"""
    message = get_accessible_message(callback.message)
    if not callback.from_user or not message:
        await callback.answer("❌ Ошибка пользователя", show_alert=True)
        await state.clear()
        return

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")
    comment = data.get("comment")
    editing_entry_id = data.get("editing_entry_id")

    if not mood_emoji:
        await callback.answer("❌ Ошибка: данные потеряны", show_alert=True)
        await state.clear()
        return

    user_id = callback.from_user.id

    try:
        with create_session() as db:
            if editing_entry_id:
                entry = get_latest_entry_for_day(
                    db, user_id=user_id, target_date=utc_now().date()
                )
                if not entry or entry.id != editing_entry_id:
                    await callback.answer(
                        "❌ Запись для редактирования не найдена", show_alert=True
                    )
                    await state.clear()
                    return
                entry = update_mood_entry(
                    db=db,
                    entry=entry,
                    mood_emoji=mood_emoji,
                    comment=comment,
                )
            else:
                entry = add_mood_entry(
                    db=db,
                    user_id=user_id,
                    mood_emoji=mood_emoji,
                    comment=comment,
                )
    except SQLAlchemyError:
        await callback.answer("❌ Не удалось сохранить запись", show_alert=True)
        await message.answer(
            "Не получилось сохранить запись в базу. Попробуй ещё раз чуть позже.",
            reply_markup=get_main_keyboard(),
        )
        return

    await state.clear()

    await message.answer(
        f"{'✅ <b>Запись обновлена!</b>' if editing_entry_id else '✅ <b>Состояние сохранено!</b>'}\n\n"
        f"🎭 {MOOD_NAMES.get(mood_emoji, mood_emoji)} {mood_emoji}\n"
        f"📝 Комментарий: {comment if comment else '—'}",
        reply_markup=get_main_keyboard(),
    )
    await message.delete()
    await callback.answer()


@router.callback_query(F.data == "confirm_edit")
async def confirm_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Возвращает к редактированию комментария"""
    await state.set_state(MoodStates.waiting_for_comment)
    message = get_accessible_message(callback.message)
    if message:
        await message.edit_text(
            "✏️ Напиши новый комментарий:",
            reply_markup=get_comment_action_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data == "confirm_cancel")
async def confirm_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отменяет создание записи"""
    await state.clear()
    message = get_accessible_message(callback.message)
    if message:
        await message.answer(
            "❌ Создание записи отменено",
            reply_markup=get_main_keyboard(),
        )
        await message.delete()
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отменяет текущее действие"""
    await state.clear()
    message = get_accessible_message(callback.message)
    if message:
        await message.answer(
            "❌ Действие отменено",
            reply_markup=get_main_keyboard(),
        )
        await message.delete()
    await callback.answer()


@router.callback_query(F.data == "cancel_to_menu")
async def cancel_to_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню при выборе состояния."""
    await state.clear()
    message = get_accessible_message(callback.message)
    if message:
        await message.answer(
            "📍 Главное меню:",
            reply_markup=get_main_keyboard(),
        )
        await message.delete()
    await callback.answer()


@router.message(F.text == "📅 История")
async def show_history(message: types.Message):
    """Показывает историю последних записей состояния."""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    with create_session() as db:
        entries = get_user_entries(db, user_id=message.from_user.id, limit=15)

    if not entries:
        await message.answer("📭 Пока нет записей состояний.")
        return

    text = "📅 <b>Твоя история состояний</b>\n\n"

    for entry in entries:
        text += f"{entry.timestamp.strftime('%d.%m %H:%M')}  {entry.mood_emoji}  "

        comment = str(entry.comment).strip() if entry.comment is not None else ""
        if comment:
            text += f"— {comment}\n"
        else:
            text += "\n"

    await message.answer(text, reply_markup=get_main_keyboard())


@router.message(F.text == "✏️ Исправить запись за сегодня")
async def edit_today_entry(message: types.Message, state: FSMContext):
    """Позволяет исправить последнюю запись за текущий день."""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    with create_session() as db:
        entry = get_latest_entry_for_day(
            db,
            user_id=message.from_user.id,
            target_date=utc_now().date(),
        )

    if not entry:
        await message.answer(
            "Сегодня ещё нет записи для редактирования. Сначала создай её через «Записать состояние».",
            reply_markup=get_main_keyboard(),
        )
        return

    await state.clear()
    await state.update_data(editing_entry_id=entry.id)
    await state.set_state(MoodStates.waiting_for_mood)

    current_comment = entry.comment.strip() if entry.comment else "—"
    await message.answer(
        f"✏️ <b>Редактируем запись за сегодня</b>\n\n"
        f"Сейчас: {MOOD_NAMES.get(entry.mood_emoji, entry.mood_emoji)} {entry.mood_emoji}\n"
        f"Комментарий: {current_comment}\n\n"
        "Выбери новое состояние:",
        reply_markup=get_mood_inline_keyboard(),
    )


@router.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message, state: FSMContext):
    """Показывает статистику по состояниям."""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    await state.set_state(StatsStates.viewing_stats)
    await state.update_data(period="week")
    await show_stats_message(message, state, "week")


async def show_stats_message(message: types.Message, state: FSMContext, period: str):
    """Формирует и отправляет сообщение со статистикой"""
    if not message.from_user:
        return

    with create_session() as db:
        stats = get_mood_statistics(db, user_id=message.from_user.id, period=period)
    await state.update_data(period=period)
    text = build_stats_text(stats, period)
    await message.answer(
        text,
        reply_markup=get_stats_period_keyboard(period),
    )


@router.callback_query(F.data.startswith("stats_period_"))
async def process_stats_period_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор периода статистики"""
    message = get_accessible_message(callback.message)
    if not callback.data or not message:
        await callback.answer()
        return

    period = callback.data.replace("stats_period_", "")
    await state.update_data(period=period)

    # Отправляем новое сообщение со статистикой
    await show_stats_message(message, state, period)
    await message.delete()
    await callback.answer()


@router.message(F.text == "🗓 Календарь")
async def show_calendar(message: types.Message):
    """Показывает календарь состояний за текущий месяц."""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    now = utc_now()
    await show_calendar_message(message, message.from_user.id, now.year, now.month)


@router.callback_query(F.data.startswith("calendar_month_"))
async def process_calendar_navigation(callback: CallbackQuery):
    """Переключает месяц в календаре."""
    message = get_accessible_message(callback.message)
    if not callback.from_user or not callback.data or not message:
        await callback.answer()
        return

    if callback.data == "calendar_month_current":
        now = utc_now()
        year, month = now.year, now.month
    else:
        _, _, year_str, month_str = callback.data.split("_")
        year, month = int(year_str), int(month_str)

    with create_session() as db:
        entries = get_entries_for_month(
            db, user_id=callback.from_user.id, year=year, month=month
        )

    text = build_calendar_text(entries, year, month)
    await message.edit_text(
        text,
        reply_markup=get_calendar_navigation_keyboard(year, month),
    )
    await callback.answer()


@router.message(Command("help"))
@router.message(F.text.in_(["❓ Помощь", "/menu"]))
async def show_menu(message: types.Message):
    """Возвращает пользователя в главное меню"""
    await message.answer(build_help_text(), reply_markup=get_main_keyboard())


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Отмена любого действия"""
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=get_main_keyboard())

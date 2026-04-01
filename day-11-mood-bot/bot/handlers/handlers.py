from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from bot.exporters import (
    create_csv_export_file,
    create_html_report_file,
    create_json_export_file,
)
from bot.keyboards.keyboards import (
    get_calendar_navigation_keyboard,
    get_cancel_inline_keyboard,
    get_comment_action_keyboard,
    get_confirm_keyboard,
    get_export_keyboard,
    get_main_keyboard,
    get_mood_inline_keyboard,
    get_reason_inline_keyboard,
    get_stats_period_keyboard,
)
from bot.states import MoodStates, StatsStates
from database.repository import (
    MOOD_SCORES,
    add_mood_entry,
    get_all_user_entries,
    get_entry_mood_key,
    get_entries_for_month,
    get_latest_entry_for_day,
    get_mood_emoji,
    get_mood_statistics,
    get_user_entries,
    normalize_mood_key,
    update_mood_entry,
    utc_now,
)
from database.session import create_session
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

router = Router()

MOOD_NAMES = {
    "excellent": "Отлично",
    "good": "Хорошо",
    "normal": "Нормально",
    "bad": "Плохо",
    "awful": "Ужасно",
}

DAY_MARKERS = {
    "excellent": "🟢",
    "good": "🟢",
    "normal": "🟡",
    "bad": "🟠",
    "awful": "🔴",
}

REASON_NAMES = {
    "family": "Семья",
    "friends": "Друзья",
    "relationships": "Отношения",
    "work": "Работа",
    "health": "Здоровье",
    "weather": "Погода",
    "sleep": "Сон",
    "money": "Деньги",
    "study": "Учёба",
    "emotions": "Эмоции",
    "other": "Другое",
    "none": "Без причины",
}

COMMENT_TEMPLATES = {
    "family": [
        ("Тепло дома", "Тепло дома"),
        ("Поддержка", "Поддержка семьи"),
        ("Семейные дела", "Семейные дела"),
        ("Напряжение", "Напряжение дома"),
        ("Разговор", "Важный разговор в семье"),
        ("Скучаю", "Скучаю по семье"),
        ("Забота", "Чувствую заботу семьи"),
        ("Переживания", "Переживания из-за семьи"),
    ],
    "friends": [
        ("Встреча", "Встреча с друзьями"),
        ("Поддержали", "Друзья поддержали"),
        ("Весело", "Хорошо провёл(а) время с друзьями"),
        ("Не хватает", "Не хватает общения с друзьями"),
        ("Неловко", "Неловкое общение"),
        ("Конфликт", "Неприятный момент с друзьями"),
        ("Созвон", "Тёплый созвон с друзьями"),
        ("Скучаю", "Скучаю по друзьям"),
    ],
    "relationships": [
        ("Близость", "Чувствую близость"),
        ("Поддержка", "Чувствую поддержку"),
        ("Общение", "Приятное общение"),
        ("Недопонимание", "Было недопонимание"),
        ("Ссора", "Ссора повлияла на состояние"),
        ("Тревога", "Тревожусь из-за отношений"),
        ("Внимание", "Хочется больше внимания"),
        ("Спокойно", "Спокойно в отношениях"),
    ],
    "work": [
        ("Продуктивно", "Продуктивный день"),
        ("Много задач", "Много задач"),
        ("Стресс", "Стресс из-за работы"),
        ("Нет сил", "Нет сил на работу"),
        ("Успех", "Доволен(а) результатом"),
        ("Сроки", "Давят сроки"),
        ("Конфликт", "Напряжение на работе"),
        ("Перегруз", "Рабочий перегруз"),
    ],
    "health": [
        ("Лучше", "Стало лучше"),
        ("Нет сил", "Нет сил"),
        ("Самочувствие", "Плохое самочувствие"),
        ("Болит", "Боль или дискомфорт"),
        ("Спокойно", "Самочувствие в норме"),
        ("Тревога", "Переживаю за здоровье"),
        ("Восстановление", "Постепенно восстанавливаюсь"),
        ("Слабость", "Чувствую слабость"),
    ],
    "weather": [
        ("Радует", "Погода радует"),
        ("Давит", "Погода давит"),
        ("Пасмурно", "Пасмурно и тяжело"),
        ("Энергия", "Погода добавила энергии"),
        ("Жара", "Тяжело из-за жары"),
        ("Холод", "Холод влияет на состояние"),
        ("Солнце", "Солнечно и легче"),
        ("Серость", "Серость за окном давит"),
    ],
    "sleep": [
        ("Выспался", "Хорошо выспался(-ась)"),
        ("Не выспался", "Не выспался(-ась)"),
        ("Усталость", "Проснулся(-ась) уставшим(-ей)"),
        ("Режим", "Сбился режим сна"),
        ("Нормально", "Спал(а) нормально"),
        ("Сонливость", "Весь день клонит в сон"),
        ("Просыпался", "Плохо спал(а) ночью"),
        ("Легче", "После сна стало легче"),
    ],
    "money": [
        ("Спокойно", "Спокойно по деньгам"),
        ("Траты", "Неожиданные траты"),
        ("Тревога", "Переживаю из-за денег"),
        ("Давление", "Давят финансовые вопросы"),
        ("Стабильно", "Есть чувство стабильности"),
        ("Расходы", "Большие расходы"),
        ("Доход", "Хорошие новости по деньгам"),
        ("Напряжно", "Финансово напряжённо"),
    ],
    "study": [
        ("Продуктивно", "Продуктивно позанимался(-ась)"),
        ("Сложно", "Трудно сосредоточиться"),
        ("Прогресс", "Есть прогресс"),
        ("Усталость", "Устал(а) от учёбы"),
        ("Тревога", "Переживаю из-за учёбы"),
        ("Удовлетворение", "Учёба дала удовлетворение"),
        ("Откладываю", "Откладываю учёбу"),
        ("Перегруз", "Учебный перегруз"),
    ],
    "emotions": [
        ("Спокойно", "Внутренне спокойно"),
        ("Тревожно", "Тревожно"),
        ("Раздражение", "Раздражение"),
        ("Легко", "Чувствую лёгкость"),
        ("Тяжело", "Эмоционально тяжело"),
        ("Радость", "Радость без причины"),
        ("Опустошение", "Чувствую опустошение"),
        ("Стабильно", "Эмоции стабильны"),
    ],
    "other": [
        ("Обычный день", "Просто такой день"),
        ("Навалилось", "Всё навалилось сразу"),
        ("Спокойно", "День прошёл спокойно"),
        ("Выбило", "Что-то выбило из колеи"),
        ("Не понял", "Не до конца понимаю почему"),
        ("Много всего", "Много всего сразу"),
        ("Сумбур", "Сумбурный день"),
        ("Фон дня", "Общий фон дня"),
    ],
    "none": [
        ("Само по себе", "Само по себе"),
        ("Без причины", "Без явной причины"),
        ("Просто так", "Просто такое состояние"),
        ("Фон дня", "Фон дня такой"),
        ("Ничего особенного", "Ничего особенного не произошло"),
        ("Не объяснить", "Не могу объяснить словами"),
        ("Как есть", "Просто как есть"),
        ("Без событий", "Без заметных событий"),
    ],
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

    entries_by_day = {}
    for entry in entries:
        day_key = entry.timestamp.strftime("%Y-%m-%d")
        entries_by_day.setdefault(day_key, []).append(entry)

    now = utc_now()
    today = now.strftime("%Y-%m-%d")
    cal = calendar.monthcalendar(year, month)

    def summarize_day(day_entries):
        scores = {}
        for day_entry in day_entries:
            mood_key = get_entry_mood_key(day_entry)
            scores[mood_key] = scores.get(mood_key, 0) + MOOD_SCORES.get(mood_key, 3)
        best_key = max(
            scores, key=lambda mood_key: (scores[mood_key], MOOD_SCORES.get(mood_key, 0))
        )
        return best_key

    day_marker_by_day = {
        day_key: DAY_MARKERS.get(summarize_day(day_entries), "⚪")
        for day_key, day_entries in entries_by_day.items()
    }

    active_days = len(entries_by_day)
    total_entries = len(entries)
    dominant_marker = None
    if day_marker_by_day:
        marker_counts = {}
        for marker in day_marker_by_day.values():
            marker_counts[marker] = marker_counts.get(marker, 0) + 1
        dominant_marker = max(marker_counts, key=lambda marker: marker_counts[marker])

    summary_bits = [
        f"записей: <b>{total_entries}</b>",
        f"активных дней: <b>{active_days}</b>",
    ]
    if dominant_marker:
        summary_bits.append(f"фон месяца: <b>{dominant_marker}</b>")

    text = f"🗓 <b>Календарь состояний — {format_month_title(year, month)}</b>\n"
    text += " · ".join(summary_bits) + "\n\n"
    text += "<pre> Пн   Вт   Ср   Чт   Пт   Сб   Вс\n"

    for week in cal:
        week_cells = []
        for day_num in week:
            if day_num == 0:
                week_cells.append("     ")
                continue

            date_str = f"{year}-{month:02d}-{day_num:02d}"
            marker = day_marker_by_day.get(date_str, "⚪")
            is_today = date_str == today and year == now.year and month == now.month
            prefix = "▣" if is_today else " "
            week_cells.append(f"{prefix}{day_num:02d}{marker}")

        text += " ".join(week_cells).rstrip() + "\n"

    text += "</pre>\n"
    text += "▣ Сегодня · 🟢 хорошо · 🟡 нормально · 🟠 тяжело · 🔴 очень тяжело · ⚪ нет записи"
    return text


def build_help_text() -> str:
    return (
        "❓ <b>Что умеет бот</b>\n\n"
        "➕ <b>Записать состояние</b> — создать новую запись.\n"
        "📊 <b>Моя статистика</b> — сводка за сегодня, неделю, месяц и всё время.\n"
        "🗓 <b>Календарь</b> — месячный обзор с переключением по месяцам.\n\n"
        "📤 <b>Экспорт</b> — отправить HTML-отчёт, CSV или JSON прямо в чат.\n\n"
        "Во время ввода комментария можно написать свой текст, выбрать шаблон или нажать <b>Пропустить</b>."
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
    reason = REASON_NAMES.get(entry.reason, "без причины") if entry.reason else "без причины"
    mood_key = get_entry_mood_key(entry)
    mood_emoji = get_mood_emoji(mood_key)
    return (
        f"{entry.timestamp.strftime('%H:%M')} · "
        f"{MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}"
        f" · {reason}"
        f" · {comment}"
    )


def build_stats_insight(stats: dict, period: str) -> str:
    """Строит короткий вывод по статистике периода."""
    dominant = stats.get("dominant_mood")
    if not dominant:
        return "Пока рано делать выводы."

    mood_label = MOOD_NAMES.get(dominant["key"]) or str(dominant["key"])
    mood_name = mood_label.lower()
    negative_reasons = stats.get("negative_reasons", [])
    positive_reasons = stats.get("positive_reasons", [])

    negative_reason_text = ""
    positive_reason_text = ""
    if negative_reasons:
        negative_reason_text = f" Сильнее всего мешали: {', '.join(REASON_NAMES.get(reason, reason) for reason, _ in negative_reasons[:2]).lower()}."
    if positive_reasons:
        positive_reason_text = f" Чаще всего поддерживали: {', '.join(REASON_NAMES.get(reason, reason) for reason, _ in positive_reasons[:2]).lower()}."

    if period == "day":
        return f"Сегодня чаще всего состояние было: {mood_name}.{negative_reason_text or positive_reason_text}"
    if period == "week":
        return f"За неделю чаще всего у тебя было состояние: {mood_name}.{negative_reason_text}{positive_reason_text}"
    if period == "month":
        return f"За месяц чаще всего повторялось состояние: {mood_name}.{negative_reason_text}{positive_reason_text}"
    return f"За всё время чаще всего встречалось состояние: {mood_name}.{negative_reason_text}{positive_reason_text}"


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
        text += f"🗓 Активных дней: <b>{stats.get('active_days', 0)}</b>\n"

        streak = stats.get("streak", 0)
        if streak > 0:
            text += f"🔥 Серия записей: <b>{streak} дн.</b>\n"

        if period == "all":
            text += f"🧭 Дней с первой записи: <b>{stats.get('tracking_days', 0)}</b>\n"

    if dominant:
        dominant_key = dominant["key"]
        text += (
            f"🏆 Чаще всего: <b>{MOOD_NAMES.get(dominant_key, dominant_key)} "
            f"{get_mood_emoji(dominant_key)}</b> ({dominant['count']} раз, {dominant['percent']}%)\n"
        )

    if period in {"month", "all"}:
        best_day = stats.get("best_day")
        worst_day = stats.get("worst_day")
        if best_day:
            text += f"🌤 Лучший день: <b>{best_day['date'].strftime('%d.%m')}</b>\n"
        if worst_day:
            text += (
                f"🌧 Самый тяжёлый день: <b>{worst_day['date'].strftime('%d.%m')}</b>\n"
            )

    top_reasons = stats.get("top_reasons", [])
    if top_reasons:
        text += "\n📌 <b>Главные причины</b>\n"
        for reason, data in top_reasons:
            reason_name = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
            text += f"{reason_name} — <b>{data['count']}</b> ({data['percent']}%)\n"

    negative_reasons = stats.get("negative_reasons", [])
    if negative_reasons:
        text += "\n🔻 <b>Что чаще тянуло вниз</b>\n"
        for reason, count in negative_reasons:
            reason_name = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
            text += f"{reason_name} — <b>{count}</b>\n"

    positive_reasons = stats.get("positive_reasons", [])
    if positive_reasons:
        text += "\n🔺 <b>Что чаще поддерживало</b>\n"
        for reason, count in positive_reasons:
            reason_name = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
            text += f"{reason_name} — <b>{count}</b>\n"

    text += "\n🎭 <b>Распределение состояний</b>\n"
    sorted_moods = sorted(
        stats["moods"].items(), key=lambda x: x[1]["count"], reverse=True
    )
    for mood_key, data in sorted_moods:
        text += (
            f"{get_mood_emoji(mood_key)} {make_bar(data['percent'])} "
            f"<b>{data['count']}</b> ({data['percent']}%)\n"
        )

    text += f"\n💡 <b>Итог:</b> {build_stats_insight(stats, period)}"
    return text


def get_reason_templates(reason: str | None) -> list[tuple[str, str]]:
    """Возвращает шаблоны комментариев для выбранной причины."""
    return COMMENT_TEMPLATES.get(reason or "none", COMMENT_TEMPLATES["other"])


def build_template_buttons(reason: str | None) -> list[tuple[str, str]]:
    """Готовит шаблоны-кнопки для выбранной причины."""
    templates = get_reason_templates(reason)
    return [
        (label, f"comment_template_{reason or 'none'}_{index}")
        for index, (label, _) in enumerate(templates)
    ]


async def show_comment_step(
    message: Message, mood_key: str, reason: str | None, reason_label: str
) -> None:
    """Показывает шаг ввода комментария."""
    template_buttons = build_template_buttons(reason)
    mood_emoji = get_mood_emoji(mood_key)
    await message.edit_text(
        f"🎭 Выбрано состояние: <b>{MOOD_NAMES.get(mood_key, mood_key)}</b> {mood_emoji}\n"
        f"📌 Причина: <b>{reason_label}</b>\n\n"
        "📝 Напиши комментарий к своему состоянию\n"
        "<i>Или выбери шаблон ниже, либо пропусти этот шаг.</i>",
        reply_markup=get_comment_action_keyboard(template_buttons),
    )


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


async def send_export_file(
    message: Message,
    file_path: Path,
    caption: str,
) -> None:
    """Отправляет файл пользователю и удаляет временный файл после отправки."""
    try:
        await message.answer_document(FSInputFile(file_path), caption=caption)
    finally:
        file_path.unlink(missing_ok=True)


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
    mood_key = normalize_mood_key(mood_emoji=mood_emoji)
    message = get_accessible_message(callback.message)

    await state.update_data(mood_key=mood_key)
    if message:
        await message.edit_text(
            f"🎭 Выбрано состояние: <b>{MOOD_NAMES.get(mood_key, mood_key)}</b> {mood_emoji}\n\n"
            "📌 Что больше всего повлияло на это состояние?\n"
            "<i>Выбери наиболее подходящую причину ниже.</i>",
            reply_markup=get_reason_inline_keyboard(),
        )
    await state.set_state(MoodStates.waiting_for_reason)
    await callback.answer()


@router.callback_query(F.data.startswith("reason_"))
async def process_reason_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор причины состояния."""
    if not callback.data:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    message = get_accessible_message(callback.message)
    reason_key = callback.data.replace("reason_", "")
    reason_label = REASON_NAMES.get(reason_key, "Другое")
    data = await state.get_data()
    mood_key = data.get("mood_key")

    await state.update_data(reason=reason_key if reason_key != "none" else None)
    if message:
        await show_comment_step(
            message,
            mood_key,
            None if reason_key == "none" else reason_key,
            reason_label,
        )
    await state.set_state(MoodStates.waiting_for_comment)
    await callback.answer()


@router.callback_query(F.data.startswith("comment_template_"))
async def process_comment_template_callback(callback: CallbackQuery, state: FSMContext):
    """Подставляет шаблонный комментарий и показывает предпросмотр."""
    message = get_accessible_message(callback.message)
    if not callback.data or not message:
        await callback.answer()
        return

    _, _, reason_key, index_str = callback.data.split("_", 3)
    templates = get_reason_templates(None if reason_key == "none" else reason_key)
    template_index = int(index_str)
    template_text = templates[template_index][1] if template_index < len(templates) else None
    if not template_text:
        await callback.answer("❌ Шаблон не найден", show_alert=True)
        return

    await state.update_data(comment=template_text)
    await state.set_state(MoodStates.waiting_for_confirm)

    data = await state.get_data()
    mood_key = data.get("mood_key")
    reason = data.get("reason")
    reason_text = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
    mood_emoji = get_mood_emoji(mood_key)

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
        f"📌 Причина: {reason_text}\n"
        f"📝 Комментарий: {template_text}\n\n"
        "Всё верно?"
    )
    if data.get("editing_entry_id"):
        preview_text = (
            "📋 <b>Проверь изменения перед сохранением:</b>\n\n"
            f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
            f"📌 Причина: {reason_text}\n"
            f"📝 Комментарий: {template_text}\n\n"
            "Обновить запись?"
        )

    await message.edit_text(
        preview_text,
        reply_markup=get_confirm_keyboard(),
    )
    await callback.answer("Шаблон подставлен")


@router.message(MoodStates.waiting_for_comment, F.text)
async def process_comment(message: types.Message, state: FSMContext):
    """Сохраняет комментарий и показывает предпросмотр"""
    comment = message.text.strip() if message.text else None

    data = await state.get_data()
    mood_key = data.get("mood_key")
    reason = data.get("reason")
    reason_text = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
    mood_emoji = get_mood_emoji(mood_key)

    if not mood_key:
        await message.answer("❌ Ошибка: данные потеряны. Начни заново.")
        await state.clear()
        return

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
        f"📌 Причина: {reason_text}\n"
        f"📝 Комментарий: {comment if comment else '—'}\n\n"
        "Всё верно?"
    )
    if data.get("editing_entry_id"):
        preview_text = (
            "📋 <b>Проверь изменения перед сохранением:</b>\n\n"
            f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
            f"📌 Причина: {reason_text}\n"
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
    mood_key = data.get("mood_key")
    reason = data.get("reason")
    reason_text = REASON_NAMES.get(reason, "Без причины") if reason else "Без причины"
    mood_emoji = get_mood_emoji(mood_key)

    if not mood_key:
        await callback.answer("❌ Ошибка: данные потеряны", show_alert=True)
        await state.clear()
        return

    preview_text = (
        "📋 <b>Проверь данные перед сохранением:</b>\n\n"
        f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
        f"📌 Причина: {reason_text}\n"
        "📝 Комментарий: —\n\n"
        "Всё верно?"
    )
    if data.get("editing_entry_id"):
        preview_text = (
            "📋 <b>Проверь изменения перед сохранением:</b>\n\n"
            f"🎭 Состояние: {MOOD_NAMES.get(mood_key, mood_key)} {mood_emoji}\n"
            f"📌 Причина: {reason_text}\n"
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
    mood_key = data.get("mood_key")
    reason = data.get("reason")
    comment = data.get("comment")
    editing_entry_id = data.get("editing_entry_id")

    if not mood_key:
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
                    mood_key=mood_key,
                    reason=reason,
                    comment=comment,
                )
            else:
                entry = add_mood_entry(
                    db=db,
                    user_id=user_id,
                    mood_key=mood_key,
                    reason=reason,
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
        f"🎭 {MOOD_NAMES.get(mood_key, mood_key)} {get_mood_emoji(mood_key)}\n"
        f"📌 Причина: {REASON_NAMES.get(reason, 'Без причины') if reason else 'Без причины'}\n"
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
    data = await state.get_data()
    mood_key = data.get("mood_key")
    reason = data.get("reason")
    if message:
        await show_comment_step(
            message,
            mood_key,
            reason,
            REASON_NAMES.get(reason, "Без причины") if reason else "Без причины",
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
        mood_key = get_entry_mood_key(entry)
        text += f"{entry.timestamp.strftime('%d.%m %H:%M')}  {get_mood_emoji(mood_key)}  "

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

    mood_key = get_entry_mood_key(entry)
    await state.clear()
    await state.update_data(editing_entry_id=entry.id)
    await state.update_data(mood_key=mood_key)
    await state.update_data(reason=entry.reason)
    await state.set_state(MoodStates.waiting_for_mood)

    current_comment = entry.comment.strip() if entry.comment else "—"
    await message.answer(
        f"✏️ <b>Редактируем запись за сегодня</b>\n\n"
        f"Сейчас: {MOOD_NAMES.get(mood_key, mood_key)} {get_mood_emoji(mood_key)}\n"
        f"Причина: {REASON_NAMES.get(entry.reason, 'Без причины') if entry.reason else 'Без причины'}\n"
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
    await show_stats_message(message, state, "week", user_id=message.from_user.id)


async def show_stats_message(
    message: types.Message, state: FSMContext, period: str, user_id: int
):
    """Формирует и отправляет сообщение со статистикой"""
    with create_session() as db:
        stats = get_mood_statistics(db, user_id=user_id, period=period)
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
    if not callback.data or not message or not callback.from_user:
        await callback.answer()
        return

    period = callback.data.replace("stats_period_", "")
    await state.update_data(period=period)

    # Отправляем новое сообщение со статистикой
    await show_stats_message(message, state, period, user_id=callback.from_user.id)
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


@router.message(Command("export"))
@router.message(F.text == "📤 Экспорт")
async def show_export_menu(message: types.Message):
    """Показывает варианты экспорта данных."""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    await message.answer(
        "📤 <b>Экспорт данных</b>\n\nВыбери удобный формат выгрузки:",
        reply_markup=get_export_keyboard(),
    )


@router.callback_query(F.data.startswith("export_"))
async def process_export_callback(callback: CallbackQuery):
    """Генерирует экспорт и отправляет файл пользователю."""
    message = get_accessible_message(callback.message)
    if not callback.from_user or not callback.data or not message:
        await callback.answer()
        return

    export_kind = callback.data.replace("export_", "")

    with create_session() as db:
        if export_kind == "html_month":
            now = utc_now()
            entries = get_entries_for_month(
                db,
                user_id=callback.from_user.id,
                year=now.year,
                month=now.month,
            )
            stats = get_mood_statistics(db, user_id=callback.from_user.id, period="month")
            file_path = create_html_report_file(
                title="Отчёт по состояниям",
                period_label=f"Текущий месяц: {now.strftime('%m.%Y')}",
                stats=stats,
                entries=entries,
                filename_prefix="mood_report_month_",
            )
            caption = "HTML-отчёт за текущий месяц"
        elif export_kind == "html_all":
            entries = get_all_user_entries(db, user_id=callback.from_user.id)
            stats = get_mood_statistics(db, user_id=callback.from_user.id, period="all")
            file_path = create_html_report_file(
                title="Полный отчёт по состояниям",
                period_label="Весь период наблюдений",
                stats=stats,
                entries=entries,
                filename_prefix="mood_report_all_",
            )
            caption = "HTML-отчёт за всё время"
        elif export_kind == "csv_all":
            entries = get_all_user_entries(db, user_id=callback.from_user.id)
            file_path = create_csv_export_file(
                entries,
                filename_prefix="mood_export_",
            )
            caption = "CSV-экспорт записей"
        elif export_kind == "json_all":
            entries = get_all_user_entries(db, user_id=callback.from_user.id)
            file_path = create_json_export_file(
                entries,
                filename_prefix="mood_export_",
            )
            caption = "JSON-экспорт записей"
        else:
            await callback.answer("Неизвестный формат экспорта", show_alert=True)
            return

    await send_export_file(message, file_path, caption)
    await callback.answer("Файл готов")


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

from aiogram import types
from aiogram.fsm.context import FSMContext
from database.repository import add_mood_entry, get_mood_statistics, get_user_entries
from database.session import get_db

# Правильные импорты
from bot.keyboards.keyboards import (
    get_cancel_keyboard,
    get_main_keyboard,
    get_mood_keyboard,
)
from bot.states import MoodStates


async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я <b>Mood</b> — твой трекер настроения.\n\n"
        "Здесь ты можешь регулярно отмечать, как себя чувствуешь, "
        "и потом смотреть свою историю и статистику.\n\n"
        "Давай начнём?",
        reply_markup=get_main_keyboard(),
    )


async def start_mood_entry(message: types.Message, state: FSMContext):
    """Начинает процесс записи настроения"""
    await message.answer(
        "Как ты сейчас себя чувствуешь?\nВыбери вариант:",
        reply_markup=get_mood_keyboard(),
    )
    await state.set_state(MoodStates.waiting_for_mood)


async def process_mood_emoji(message: types.Message, state: FSMContext):
    """Обрабатывает выбор настроения"""
    if not message.text:
        await message.answer("Пожалуйста, выбери вариант из кнопок.")
        return

    # Берём только эмодзи (первый символ)
    mood_emoji = message.text[0]

    await state.update_data(mood_emoji=mood_emoji)
    await message.answer(
        "📝 Напиши комментарий к своему настроению (или отправь '-' чтобы пропустить):",
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(MoodStates.waiting_for_comment)


async def process_comment(message: types.Message, state: FSMContext):
    """Сохраняет запись настроения"""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        await state.clear()
        return

    comment = message.text.strip() if message.text and message.text != "-" else None

    data = await state.get_data()
    mood_emoji = data.get("mood_emoji")

    if not mood_emoji:
        await message.answer("Что-то пошло не так. Попробуй заново.")
        await state.clear()
        return

    db = next(get_db())
    add_mood_entry(
        db=db,
        user_id=message.from_user.id,
        mood_emoji=mood_emoji,
        tags=None,
        comment=comment,
    )

    await state.clear()

    await message.answer(
        f"✅ Настроение сохранено!\n\n"
        f"Настроение: {mood_emoji}\n"
        f"Комментарий: {comment if comment else '—'}",
        reply_markup=get_main_keyboard(),
    )


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


async def show_stats(message: types.Message):
    """Показывает статистику настроения"""
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return

    db = next(get_db())
    stats = get_mood_statistics(db, user_id=message.from_user.id)

    if stats["total"] == 0:  # ← изменили с "count" на "total"
        await message.answer(
            "📭 Пока нет данных для статистики.\nДобавь несколько записей настроения."
        )
        return

    text = "📊 <b>Твоя статистика настроения</b>\n\n"
    text += f"📌 Всего записей: <b>{stats['total']}</b>\n"
    text += f"📈 Среднее в день: <b>{stats['avg_per_day']}</b>\n\n"
    text += "🔢 Самые частые настроения:\n"

    sorted_moods = sorted(stats["moods"].items(), key=lambda x: x[1], reverse=True)
    for emoji, count in sorted_moods[:10]:
        text += f"{emoji} — {count} раз\n"

    await message.answer(text, reply_markup=get_main_keyboard())


async def cancel_handler(message: types.Message, state: FSMContext):
    """Отмена любого действия"""
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=get_main_keyboard())
    

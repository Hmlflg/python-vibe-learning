import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from database import get_db
from dotenv import load_dotenv
from keyboards import (
    get_cancel_keyboard,  # если ещё не импортировано
    get_main_keyboard,
)
from repository import add_expense, get_all_expenses, get_statistics
from sqlalchemy.orm import Session

load_dotenv()

bot_token_raw = os.getenv("BOT_TOKEN")
if not bot_token_raw:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

BOT_TOKEN: str = bot_token_raw  # type: ignore[assignment]  # Явно приводим к str после проверки

DATA_FILE = Path("expenses.json")

# ==================== НАСТРОЙКА ПРОКСИ ====================
# Попробуем подключиться через разные прокси
PROXIES = [
    ("socks5://127.0.0.1:10808", "Blacktemple SOCKS5"),
    ("http://127.0.0.1:2080", "VPN HTTP 2080"),
    (None, "Без прокси"),
]

dp = Dispatcher()

# Хранилище состояний пользователя
user_data = {}


# def load_expenses() -> list[dict]:
#     if DATA_FILE.exists():
#         try:
#             with open(DATA_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except Exception:
#             return []
#     return []


# def save_expenses(expenses: list[dict]):
#     with open(DATA_FILE, "w", encoding="utf-8") as f:
#         json.dump(expenses, f, ensure_ascii=False, indent=2)


# Хранилище состояний пользователя
user_data = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я твой бот для учёта расходов.\n\nВыбери действие:",
        reply_markup=get_main_keyboard(),
    )


@dp.message(lambda m: m.text == "📋 Все расходы")
async def show_all_expenses(message: types.Message):
    db = next(get_db())
    expenses = get_all_expenses(db, limit=15)

    if not expenses:
        await message.answer("📭 Пока нет расходов.")
        return

    text = "📋 <b>Последние расходы:</b>\n\n"
    for exp in expenses:
        text += f"• {exp.date.strftime('%Y-%m-%d %H:%M')} | <b>{exp.category}</b> | {exp.amount} руб.\n"

        # Надёжное извлечение описания
        description = (
            str(exp.description).strip() if exp.description is not None else ""
        )
        if description:
            text += f"  📝 {description}\n"

        text += "\n"

    await message.answer(text)


@dp.message(lambda m: m.text == "📊 Статистика")
async def show_stats(message: types.Message):
    db = next(get_db())
    stats = get_statistics(db)

    text = (
        "📊 <b>Статистика расходов</b>\n\n"
        f"💰 Всего записей: <b>{stats['count']}</b>\n"
        f"💵 Общая сумма: <b>{stats['total']}</b> руб.\n"
        f"📈 Средний расход: <b>{stats['avg']}</b> руб.\n\n"
        "📂 По категориям:\n"
    )

    for cat, amount in sorted(
        stats["categories"].items(), key=lambda x: x[1], reverse=True
    ):
        text += f"• {cat}: <b>{amount:.2f}</b> руб.\n"

    await message.answer(text)


@dp.message(lambda m: m.text == "➕ Добавить расход")
async def start_add_expense(message: types.Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    user_data[user_id] = {"step": "category"}
    await message.answer(
        "💸 Введите категорию расхода:\n"
        "(например: Еда, Транспорт, Развлечения, Техника)",
        reply_markup=get_cancel_keyboard(),
    )


@dp.message(Command("cancel"))
@dp.message(lambda m: m.text == "❌ Отмена")
async def cancel_handler(message: types.Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await message.answer(
        "❌ Добавление расхода отменено.", reply_markup=get_main_keyboard()
    )


@dp.message()
async def handle_input(message: types.Message):
    if not message.from_user or not message.text:
        return
    user_id = message.from_user.id
    if user_id not in user_data:
        return

    state = user_data[user_id]
    text = message.text.strip()

    if state["step"] == "category":
        state["category"] = text.strip().capitalize()  # нормализация категории
        state["step"] = "amount"
        await message.answer(
            "💵 Введите сумму расхода:", reply_markup=get_cancel_keyboard()
        )

    elif state["step"] == "amount":
        try:
            amount = float(text.replace(",", "."))
            if amount <= 0:
                raise ValueError
            state["amount"] = amount
            state["step"] = "description"
            await message.answer(
                "📝 Введите описание (или '-' для пропуска):",
                reply_markup=get_cancel_keyboard(),
            )
        except ValueError:
            await message.answer(
                "❌ Введите корректную сумму (например: 500 или 1250.50)",
                reply_markup=get_cancel_keyboard(),
            )

    elif state["step"] == "description":
        description = "" if text == "-" else text

        db = next(get_db())  # ← новая строка
        add_expense(db, state["category"], state["amount"], description)

        del user_data[user_id]

        await message.answer(
            "✅ Расход добавлен успешно!", reply_markup=get_main_keyboard()
        )


async def main():
    global bot
    bot = None
    for proxy_url, name in PROXIES:
        try:
            print(f"🔍 Пробую подключиться: {name}")
            if proxy_url:
                session = AiohttpSession(proxy=proxy_url)
                bot = Bot(
                    token=BOT_TOKEN,
                    session=session,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
                )
            else:
                bot = Bot(
                    token=BOT_TOKEN,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
                )
            await bot.get_me()  # проверка подключения
            print(f"✅ Успешно подключено через: {name}")
            break
        except Exception:
            continue

    if bot is None:
        raise Exception("Не удалось подключиться к Telegram")

    print("🤖 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

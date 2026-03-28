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
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

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


def load_expenses() -> list[dict]:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_expenses(expenses: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=2)


def get_main_keyboard():
    kb = [
        [KeyboardButton(text="➕ Добавить расход")],
        [KeyboardButton(text="📋 Все расходы")],
        [KeyboardButton(text="📊 Статистика")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


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
    expenses = load_expenses()
    if not expenses:
        await message.answer("Пока нет расходов.")
        return

    text = "📋 <b>Последние расходы:</b>\n\n"
    for exp in reversed(expenses[-10:]):
        text += f"• {exp.get('date')} | <b>{exp.get('category')}</b> | {exp.get('amount')} руб.\n"
        if exp.get("description"):
            text += f"  {exp.get('description')}\n"
        text += "\n"
    await message.answer(text)


@dp.message(lambda m: m.text == "📊 Статистика")
async def show_stats(message: types.Message):
    expenses = load_expenses()
    if not expenses:
        await message.answer("Нет данных для статистики.")
        return

    total = sum(exp.get("amount", 0) for exp in expenses)
    count = len(expenses)
    avg = round(total / count, 2) if count > 0 else 0

    text = f"📊 <b>Статистика</b>\n\nВсего: {count}\nСумма: {total:.2f} руб.\nСредний: {avg:.2f} руб."
    await message.answer(text)


@dp.message(lambda m: m.text == "➕ Добавить расход")
async def start_add_expense(message: types.Message):
    if not message.from_user:
        return
    user_id = message.from_user.id
    user_data[user_id] = {"step": "category"}
    await message.answer(
        "💸 Введите категорию расхода:\n(например: Еда, Транспорт, Развлечения)"
    )


@dp.message(Command("cancel"))
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
        state["category"] = text
        state["step"] = "amount"
        await message.answer("💵 Введите сумму:")

    elif state["step"] == "amount":
        try:
            amount = float(text.replace(",", "."))
            if amount <= 0:
                raise ValueError
            state["amount"] = amount
            state["step"] = "description"
            await message.answer("📝 Введите описание (или '-' для пропуска):")
        except ValueError:
            await message.answer("❌ Введите корректную сумму.")

    elif state["step"] == "description":
        description = "" if text == "-" else text

        expenses = load_expenses()
        new_expense = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "category": state["category"],
            "amount": state["amount"],
            "description": description,
        }
        expenses.append(new_expense)
        save_expenses(expenses)

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

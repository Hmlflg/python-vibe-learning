import asyncio

import config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers.handlers import (
    cancel_handler,
    cmd_start,
    process_comment,
    process_mood_emoji,
    show_history,
    show_stats,
    start_mood_entry,
)
from bot.states import MoodStates


async def main():
    print("🤖 Запуск бота Mood...")

    bot = None
    for proxy_url, name in config.PROXIES:
        try:
            print(f"🔍 Пробую подключиться: {name}")

            if proxy_url:
                session = AiohttpSession(proxy=proxy_url)
                bot = Bot(
                    token=config.BOT_TOKEN,  # type: ignore[arg-type]
                    session=session,
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
                )
            else:
                bot = Bot(
                    token=config.BOT_TOKEN,  # type: ignore[arg-type]
                    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
                )

            await bot.get_me()
            print(f"✅ Успешно подключено через: {name}")
            break

        except Exception as e:
            print(f"❌ Не удалось через {name}: {str(e)[:80]}")
            continue

    if bot is None:
        raise Exception("❌ Не удалось подключиться к Telegram ни через один прокси")

    # Настройка FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация обработчиков
    dp.message.register(cmd_start, lambda m: m.text == "/start")
    dp.message.register(start_mood_entry, lambda m: m.text == "➕ Записать настроение")
    dp.message.register(show_history, lambda m: m.text == "📅 История")
    dp.message.register(show_stats, lambda m: m.text == "📊 Моя статистика")
    dp.message.register(process_mood_emoji, MoodStates.waiting_for_mood)
    dp.message.register(process_comment, MoodStates.waiting_for_comment)
    dp.message.register(cancel_handler, lambda m: m.text == "❌ Отмена")

    print("✅ Бот Mood готов к работе!")
    print("🏃 Ожидает сообщений от пользователей...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен вручную")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

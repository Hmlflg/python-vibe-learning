import asyncio
import logging

import config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers.handlers import router
from bot.states import MoodStates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🤖 Запуск бота Mood...")

    bot = None
    for proxy_url, name in config.PROXIES:
        try:
            logger.info(f"🔍 Пробую подключиться: {name}")

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
            logger.info(f"✅ Успешно подключено через: {name}")
            break

        except Exception as e:
            logger.warning(f"❌ Не удалось через {name}: {str(e)[:80]}")
            continue

    if bot is None:
        raise Exception("❌ Не удалось подключиться к Telegram ни через один прокси")

    # Настройка FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутера
    dp.include_router(router)

    logger.info("✅ Бот Mood готов к работе!")
    logger.info("🏃 Ожидает сообщений от пользователей...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен вручную")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

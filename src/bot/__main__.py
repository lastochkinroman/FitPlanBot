"""Точка входа для бота"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Проверяем токен
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN not found")
        return

    logger.info("Starting FitPlanBot...")

    # Создаём бота и диспетчер
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем middleware
    from src.bot.middlewares.acl import SubscriptionMiddleware
    from src.bot.middlewares.logging import LoggingMiddleware

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(SubscriptionMiddleware())

    # Подключаем роутеры
    from src.bot.dialogs.questionnaire import questionnaire_dialog
    from src.bot.handlers import menu, profile, start, workouts

    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(workouts.router)
    dp.include_router(questionnaire_dialog)

    # Настраиваем диалоги
    setup_dialogs(dp)

    # Устанавливаем команды бота
    from aiogram.types import BotCommand

    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/profile", description="Профиль"),
        BotCommand(command="/cancel", description="Отменить"),
    ]
    await bot.set_my_commands(commands)

    # Запускаем бота
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

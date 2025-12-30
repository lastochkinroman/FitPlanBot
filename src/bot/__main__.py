import asyncio
import os
import logging
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram_dialog import setup_dialogs
# Импортируем настройки БД
from src.database.session import engine, Base
# Импортируем middleware
from src.bot.middlewares.logging import LoggingMiddleware
from src.bot.middlewares.stats import StatsMiddleware
from src.bot.middlewares.acl import ACLMiddleware
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

async def setup_bot_commands(bot: Bot):
    """
    Устанавливает команды бота в меню Telegram
    """
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Помощь и инструкции"),
        BotCommand(command="/profile", description="Мой профиль"),
        BotCommand(command="/cancel", description="Отменить текущее действие"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands set up")

async def create_tables():
    """
    Создаёт таблицы в БД (для разработки)
    """
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Осторожно: удаляет все таблицы!
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")

async def main():
    logger.info("Starting FitPlanBot...")
    
    # Проверяем токен
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN not found in .env file!")
        return
    
    # Создаём таблицы (только для разработки)
    await create_tables()
    
    # Создаём бота и диспетчер
    bot = Bot(token=token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем middleware
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(StatsMiddleware())
    dp.update.middleware(ACLMiddleware())
    
    logger.info("Middlewares registered")
    
    # Настраиваем команды бота
    await setup_bot_commands(bot)
    
    # Импортируем и подключаем роутеры
    from src.bot.handlers.start import router as start_router
    from src.bot.handlers.menu import router as menu_router
    from src.bot.handlers.profile import router as profile_router
    from src.bot.handlers.workouts import router as workouts_router

    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(workouts_router)
    
    logger.info("Routers included")
    logger.info("Bot is starting polling...")
    
    from src.bot.dialogs.questionnaire import questionnaire_dialog
    
    dp.include_router(questionnaire_dialog)
    setup_dialogs(dp)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())

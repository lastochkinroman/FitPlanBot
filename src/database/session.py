"""Настройка подключения к базе данных"""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "fitplanbot")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# Создаем движок с подключением к пулу
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "False").lower() == "true",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    connect_args={
        "server_settings": {
            "application_name": "fitplanbot",
        },
        "timeout": 30,  # Таймаут соединения в секундах
        "command_timeout": 60,  # Таймаут выполнения команды
    },
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """
    Генератор для получения асинхронной сессии БД

    Использование:
    async with get_session() as session:
        # работа с БД
    """
    async with async_session_maker() as session:
        yield session

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

# Создаём базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Создаём engine для подключения к PostgreSQL
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для логов SQL

# Создаём фабрику сессий
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Функция для получения сессии (будет использоваться в dependency injection)
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
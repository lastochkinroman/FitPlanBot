"""Репозиторий для работы с пользователями"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import User, UserProfile


class UserRepository:
    """Репозиторий для работы с таблицей users"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """
        Находит пользователя по telegram_id
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, **kwargs) -> User:
        """
        Создает нового пользователя
        """
        user = User(telegram_id=telegram_id, **kwargs)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, telegram_id: int, **kwargs) -> tuple[User, bool]:
        """
        Получает или создает пользователя

        Returns:
            tuple[User, bool]: (пользователь, создан_ли_новый)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user, False

        user = await self.create(telegram_id, **kwargs)
        return user, True

    async def update(self, user_id: str, **kwargs) -> User | None:
        """
        Обновляет данные пользователя
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)

        return user

    async def get_with_profile(
        self, telegram_id: int
    ) -> tuple[User | None, UserProfile | None]:
        """
        Получает пользователя с профилем
        """
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.profile))
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        return (user, user.profile) if user else (None, None)

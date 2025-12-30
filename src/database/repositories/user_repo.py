from sqlalchemy.orm import selectinload
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.database.models import User, UserProfile
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Находит пользователя по telegram_id
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, **kwargs) -> User:
        """
        Создаёт нового пользователя
        """
        user = User(telegram_id=telegram_id, **kwargs)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Created new user with telegram_id: {telegram_id}")
        return user

    async def get_or_create(self, telegram_id: int, **kwargs) -> tuple[User, bool]:
        """
        Получает существующего пользователя или создаёт нового
        Возвращает (user, is_created)
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user, False
        
        user = await self.create(telegram_id, **kwargs)
        return user, True

    async def update_username(self, telegram_id: int, username: str) -> Optional[User]:
        """
        Обновляет username пользователя
        """
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.telegram_username = username
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Updated username for user {telegram_id}: {username}")
        return user

    async def get_user_with_profile(self, telegram_id: int) -> Optional[tuple[User, Optional[UserProfile]]]:
        """
        Получает пользователя вместе с его профилем (если есть)
        """
        stmt = select(User).where(User.telegram_id == telegram_id).options(
            selectinload(User.profile)
        )
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            return user, user.profile
        return None, None
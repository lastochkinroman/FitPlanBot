"""Репозиторий для работы с подписками"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Subscription


class SubscriptionRepository:
    """Репозиторий для работы с таблицей subscriptions"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_subscription(self, user_id: str) -> Optional[Subscription]:
        """
        Получает активную подписку пользователя
        """
        now = datetime.utcnow()
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.starts_at <= now,
            Subscription.ends_at >= now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_subscription(self, user_id: str) -> Optional[Subscription]:
        """
        Получает ожидающую подписку пользователя
        """
        stmt = select(Subscription).where(
            Subscription.user_id == user_id, Subscription.status == "pending"
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_pending(self, user_id: str) -> Subscription:
        """
        Создает новую подписку в статусе pending
        """
        # Проверяем существующую pending подписку
        existing = await self.get_pending_subscription(user_id)
        if existing:
            return existing

        subscription = Subscription(user_id=user_id, status="pending")
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def activate(self, subscription_id: str, admin_id: str) -> bool:
        """
        Активирует подписку (30 дней)
        """
        now = datetime.utcnow()
        ends_at = now + timedelta(days=30)

        stmt = (
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(
                status="active",
                activated_by_admin=True,
                activated_at=now,
                starts_at=now,
                ends_at=ends_at,
            )
        )

        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def get_pending_subscriptions(self) -> List[Subscription]:
        """
        Получает все ожидающие подписки
        """
        stmt = select(Subscription).where(Subscription.status == "pending")
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Получает все подписки пользователя
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

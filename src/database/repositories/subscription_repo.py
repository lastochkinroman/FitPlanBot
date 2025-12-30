from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta
from src.database.models import Subscription, User
import logging

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_for_user(self, user_id: str) -> Optional[Subscription]:
        """
        Получает активную подписку пользователя (самую свежую)
        """
        now = datetime.utcnow()
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == 'active',
            Subscription.starts_at <= now,
            Subscription.ends_at >= now
        ).order_by(Subscription.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()  # Возвращает первый объект или None

    async def get_pending_for_user(self, user_id: str) -> Optional[Subscription]:
        """
        Получает ожидающую подписку пользователя
        """
        stmt = select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == 'pending'
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_pending(self, user_id: str) -> Subscription:
        """
        Создаёт новую подписку в статусе pending
        """
        # Проверяем, нет ли уже pending подписки
        existing = await self.get_pending_for_user(user_id)
        if existing:
            return existing

        subscription = Subscription(
            user_id=user_id,
            status='pending'
        )
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        logger.info(f"Created pending subscription for user {user_id}")
        return subscription

    async def activate_subscription(self, subscription_id: str, admin_user_id: str) -> bool:
        """
        Активирует подписку (для админа)
        """
        # Для MVP активируем на 30 дней
        starts_at = datetime.utcnow()
        ends_at = starts_at + timedelta(days=30)

        stmt = (
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(
                status='active',
                activated_by_admin=True,
                activated_at=starts_at,
                starts_at=starts_at,
                ends_at=ends_at
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()

        if result.rowcount > 0:
            logger.info(f"Activated subscription {subscription_id} by admin {admin_user_id}")
            return True
        return False

    async def get_all_pending(self) -> List[Subscription]:
        """
        Получает все ожидающие подписки (для админа)
        """
        stmt = select(Subscription).where(Subscription.status == 'pending')
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        Получает все подписки пользователя
        """
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

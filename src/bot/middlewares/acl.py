"""Middleware для проверки подписки пользователя"""

import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from sqlalchemy import select

from src.database.models import Subscription, User
from src.database.session import async_session_maker

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """
    Проверяет наличие активной подписки для доступа к платным функциям

    Шаг 113-116: Middleware для проверки подписки
    """

    # Действия, доступные без подписки (Шаг 114)
    FREE_ACCESS = {
        "commands": [
            "/start",
            "/help",
            "/cancel",
            "/profile",
            "/me",
            "/about",
            "/version",
            "/status",
            "/subscription",
            "/my_subscription",
        ],
        "texts": [
            "📝 Заполнить анкету",
            "👤 Мой профиль",
            "💳 Купить подписку",
            "⚙️ Настройки",
        ],
    }

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем сообщение или callback
        message = None
        if event.message:
            message = event.message
        elif event.callback_query:
            message = event.callback_query.message

        if not message or not hasattr(message, "text"):
            return await handler(event, data)

        text = message.text if message.text else ""

        # Проверяем, доступно ли действие без подписки (Шаг 114)
        if self._is_free_access(text):
            return await handler(event, data)

        # Проверяем активную подписку (Шаг 115)
        user_id = message.from_user.id
        has_active_subscription = await self._check_subscription(user_id)

        if not has_active_subscription:
            # Блокируем доступ (Шаг 116)
            await self._show_subscription_required(message)
            return

        # Если подписка есть - пропускаем дальше
        return await handler(event, data)

    def _is_free_access(self, text: str) -> bool:
        """Проверяет, доступно ли действие без подписки"""
        # Проверяем команды
        for command in self.FREE_ACCESS["commands"]:
            if text.startswith(command):
                return True

        # Проверяем тексты кнопок
        if text in self.FREE_ACCESS["texts"]:
            return True

        # Callback-запросы на подписку
        if text and "request_subscription" in text:
            return True

        return False

    async def _check_subscription(self, telegram_id: int) -> bool:
        """Проверяет наличие активной подписки у пользователя"""
        try:
            async with async_session_maker() as session:
                # Находим пользователя
                stmt_user = select(User).where(User.telegram_id == telegram_id)
                user = (await session.execute(stmt_user)).scalar_one_or_none()

                if not user:
                    return False

                # Проверяем активную подписку
                now = datetime.utcnow()
                stmt_sub = select(Subscription).where(
                    Subscription.user_id == user.id,
                    Subscription.status == "active",
                    Subscription.starts_at <= now,
                    Subscription.ends_at >= now,
                )

                subscription = (await session.execute(stmt_sub)).scalar_one_or_none()

                return subscription is not None

        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False

    async def _show_subscription_required(self, message: Message):
        """Показывает сообщение о необходимости подписки"""
        from src.bot.keyboards.main_menu import get_main_menu_kb

        response = (
            "🔒 <b>Требуется подписка</b>\n\n"
            "Для доступа к этому разделу нужна активная подписка.\n\n"
            "✨ <b>Что дает подписка:</b>\n"
            "✅ Персональные планы тренировок\n"
            "✅ Индивидуальное питание\n"
            "✅ Умные напоминания\n"
            "✅ Отслеживание прогресса\n\n"
            "💳 <b>Как получить подписку:</b>\n"
            "1. Нажмите кнопку <b>'💳 Купить подписку'</b>\n"
            "2. Запросите активацию\n"
            "3. Администратор активирует подписку в течение 24 часов\n\n"
            "🎯 <b>После активации вы получите доступ ко всем функциям!</b>"
        )

        await message.answer(
            text=response, parse_mode="HTML", reply_markup=get_main_menu_kb()
        )

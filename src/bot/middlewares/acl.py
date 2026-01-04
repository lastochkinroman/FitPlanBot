"""Middleware для проверки подписки пользователя"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from src.database.repositories.subscription_repo import SubscriptionRepository
from src.database.repositories.user_repo import UserRepository
from src.database.session import async_session_maker


class SubscriptionMiddleware(BaseMiddleware):
    """
    Проверяет наличие активной подписки для доступа к платным функциям
    """

    # Команды и кнопки, доступные без подписки
    FREE_ACCESS = {
        "commands": ["/start", "/help", "/cancel", "/profile", "/about"],
        "buttons": ["📝 Заполнить анкету", "👤 Мой профиль", "💳 Купить подписку"],
    }

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем сообщение
        message: Message = (
            event.message or event.callback_query.message
            if event.callback_query
            else None
        )

        if not message or not message.text:
            return await handler(event, data)

        # Проверяем, доступно ли без подписки
        text = message.text.strip()

        if self._is_free_access(text):
            return await handler(event, data)

        # Проверяем подписку
        async with async_session_maker() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(message.from_user.id)

            if not user:
                return await handler(event, data)

            sub_repo = SubscriptionRepository(session)
            subscription = await sub_repo.get_active_subscription(user.id)

            if not subscription:
                await message.answer(
                    "❌ <b>Требуется подписка</b>\n\n"
                    "Для доступа к этому функционалу нужна активная подписка.\n"
                    "Нажмите <b>💳 Купить подписку</b> для отправки заявки.",
                    parse_mode="HTML",
                )
                return

        return await handler(event, data)

    def _is_free_access(self, text: str) -> bool:
        """Проверяет, доступно ли действие без подписки"""
        # Проверяем команды
        if any(text.startswith(cmd) for cmd in self.FREE_ACCESS["commands"]):
            return True

        # Проверяем кнопки
        if text in self.FREE_ACCESS["buttons"]:
            return True

        return False

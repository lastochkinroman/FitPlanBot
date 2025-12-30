from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy import select

from src.database.session import async_session_maker
from src.database.models import Subscription


class ACLMiddleware(BaseMiddleware):
    """
    Middleware для проверки прав доступа (подписка)
    """
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Если нет сообщения (например, callback query) — пропускаем
        if not event.message or not event.message.text:
            return await handler(event, data)

        message = event.message
        text = message.text

        # Список команд, доступных без подписки
        free_commands = ['/start', '/help', '/cancel', '/profile']

        # Если это команда из свободного списка — пропускаем
        if any(text.startswith(cmd) for cmd in free_commands):
            return await handler(event, data)

        # Если это текстовая кнопка из свободных действий
        free_buttons = ['📝 Заполнить анкету', '👤 Мой профиль', '💳 Купить подписку']
        if text in free_buttons:
            return await handler(event, data)

        # Проверяем подписку в БД
        from src.database.repositories.subscription_repo import SubscriptionRepository
        from src.database.session import async_session_maker

        async with async_session_maker() as session:
            repo = SubscriptionRepository(session)
            subscription = await repo.get_active_for_user(str(message.from_user.id))

            if not subscription:
                await message.answer(
                    "❌ <b>Для доступа к этому функционалу нужна активная подписка.</b>\n\n"
                    "💳 Нажмите <b>'Купить подписку'</b> для отправки заявки на активацию.\n\n"
                    "<i>После подтверждения администратором вы получите полный доступ ко всем функциям бота.</i>",
                    parse_mode="HTML"
                )
                return

        return await handler(event, data)

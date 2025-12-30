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
        
        # TODO: Для MVP пока пропускаем всех
        # Позже здесь будет проверка подписки в БД
        # async with async_session_maker() as session:
        #     stmt = select(Subscription).where(
        #         Subscription.user_id == message.from_user.id,
        #         Subscription.status == 'active'
        #     )
        #     result = await session.execute(stmt)
        #     subscription = result.scalar_one_or_none()
            
        #     if not subscription:
        #         await message.answer(
        #             "❌ Для доступа к этому функционалу нужна подписка.\n"
        #             "Нажмите '💳 Купить подписку' для активации."
        #         )
        #         return
        
        return await handler(event, data)
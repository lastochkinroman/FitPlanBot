"""Middleware для сбора статистики"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update


class StatsMiddleware(BaseMiddleware):
    """Считает количество сообщений и callback'ов"""

    def __init__(self):
        super().__init__()
        self.total = 0  # Общий счетчик

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        self.total += 1

        # Логируем каждые 20 событий
        if self.total % 20 == 0:
            print(f"📊 Обработано событий: {self.total}")

        return await handler(event, data)

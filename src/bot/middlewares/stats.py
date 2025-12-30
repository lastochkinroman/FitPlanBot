from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update


class StatsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.message_count = 0
        self.callback_count = 0
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Собираем статистику
        if event.message:
            self.message_count += 1
        elif event.callback_query:
            self.callback_count += 1
        
        # Можно сохранять статистику в БД или кэш
        # Пока просто логируем каждые 10 сообщений
        if self.message_count % 10 == 0 and self.message_count > 0:
            print(f"📊 Stats: Messages={self.message_count}, Callbacks={self.callback_count}")
        
        return await handler(event, data)
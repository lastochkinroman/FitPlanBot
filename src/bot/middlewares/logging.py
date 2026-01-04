"""Middleware для логирования событий бота"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Логирует входящие события и время их обработки"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        start = time.time()

        # Логируем входящее событие
        log_data = self._get_event_info(event)
        logger.info(f"📥 Incoming: {log_data}")

        try:
            result = await handler(event, data)
            elapsed = time.time() - start
            logger.info(f"✅ Processed in {elapsed:.2f}s")
            return result

        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"❌ Error after {elapsed:.2f}s: {e}")
            raise

    def _get_event_info(self, event: Update) -> str:
        """Формирует информацию о событии для логов"""
        if event.message:
            msg = event.message
            user = msg.from_user
            info = f"Message from {user.id}"

            if msg.text:
                text = msg.text[:30] + "..." if len(msg.text) > 30 else msg.text
                info += f": {text}"
            elif msg.content_type:
                info += f" [{msg.content_type}]"

        elif event.callback_query:
            cb = event.callback_query
            user = cb.from_user
            info = f"Callback from {user.id}: {cb.data}"

        else:
            info = f"Unknown event: {event.update_id}"

        return info

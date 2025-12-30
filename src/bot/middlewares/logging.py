import logging
import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Определяем тип события
        if event.message:
            message = event.message
            user = message.from_user
            log_message = (
                f"📨 Message from user_id={user.id} "
                f"(@{user.username or 'no_username'}): "
            )
            
            if message.text:
                log_message += f"text='{message.text[:50]}...'"
            elif message.photo:
                log_message += f"photo ({len(message.photo)} sizes)"
            elif message.document:
                log_message += f"document: {message.document.file_name}"
            else:
                log_message += f"type={message.content_type}"
                
        elif event.callback_query:
            callback = event.callback_query
            user = callback.from_user
            log_message = (
                f"🔄 Callback from user_id={user.id} "
                f"(@{user.username or 'no_username'}): "
                f"data='{callback.data}'"
            )
        elif event.edited_message:
            log_message = f"✏️ Edited message"
        elif event.channel_post:
            log_message = f"📢 Channel post"
        else:
            log_message = f"📊 Unknown event type in update"
        
        logger.info(log_message)
        
        try:
            # Пропускаем событие дальше по цепочке middleware
            result = await handler(event, data)
            
            # Логируем время обработки
            processing_time = time.time() - start_time
            logger.info(f"✅ Event processed in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Логируем ошибки
            logger.error(f"❌ Error processing event: {e}", exc_info=True)
            raise
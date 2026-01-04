"""Клавиатуры для работы с подписками"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для запроса подписки

    Шаг 111: Кнопка "Запросить активацию"
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ Запросить активацию", callback_data="request_subscription"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="❌ Отмена", callback_data="cancel_subscription_request"
        )
    )

    return builder.as_markup()


def get_subscription_status_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления подпиской"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🔄 Обновить статус", callback_data="refresh_subscription_status"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="📋 Подробнее о подписке", callback_data="subscription_info"
        )
    )

    return builder.as_markup()

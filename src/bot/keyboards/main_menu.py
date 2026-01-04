"""Клавиатуры главного меню бота"""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Главное меню в виде клавиатуры (2 кнопки в ряду)

    Returns:
        ReplyKeyboardMarkup: Готовое меню
    """
    buttons = [
        ("📝 Заполнить анкету", "👤 Мой профиль"),
        ("🏋️ Мой план", "🍎 Питание"),
        ("⚙️ Настройки", "💳 Купить подписку"),
    ]

    builder = ReplyKeyboardBuilder()

    for row in buttons:
        for text in row:
            builder.add(KeyboardButton(text=text))

    # 2 кнопки в каждом ряду
    builder.adjust(2, 2, 2)

    return builder.as_markup(resize_keyboard=True)


# Опционально: минимальная клавиатура для пользователей без подписки
def get_basic_menu_kb() -> ReplyKeyboardMarkup:
    """
    Базовая клавиатура для пользователей без подписки
    """
    buttons = [
        ("📝 Заполнить анкету", "👤 Мой профиль"),
        ("💳 Купить подписку",),
    ]

    builder = ReplyKeyboardBuilder()

    for row in buttons:
        for text in row:
            builder.add(KeyboardButton(text=text))

    builder.adjust(2, 1)

    return builder.as_markup(resize_keyboard=True)


# Опционально: клавиатура для пользователей с активной подпиской
def get_premium_menu_kb() -> ReplyKeyboardMarkup:
    """
    Расширенная клавиатура для пользователей с подпиской
    """
    buttons = [
        ("🏋️ Мой план", "🍎 Питание"),
        ("📊 Прогресс", "📈 Статистика"),
        ("⚙️ Настройки", "👤 Профиль"),
    ]

    builder = ReplyKeyboardBuilder()

    for row in buttons:
        for text in row:
            builder.add(KeyboardButton(text=text))

    builder.adjust(2, 2, 2)

    return builder.as_markup(resize_keyboard=True)

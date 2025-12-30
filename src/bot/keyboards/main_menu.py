from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    """
    Создаёт главное меню в виде Reply-клавиатуры
    """
    builder = ReplyKeyboardBuilder()
    
    # Первый ряд: Анкета и Профиль
    builder.add(KeyboardButton(text="📝 Заполнить анкету"))
    builder.add(KeyboardButton(text="👤 Мой профиль"))
    
    # Второй ряд: План тренировок и Питание
    builder.add(KeyboardButton(text="🏋️ Мой план"))
    builder.add(KeyboardButton(text="🍎 Питание"))
    
    # Третий ряд: Настройки и Подписка
    builder.add(KeyboardButton(text="⚙️ Настройки"))
    builder.add(KeyboardButton(text="💳 Купить подписку"))
    
    # Настраиваем расположение: 2 кнопки в каждом ряду
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(resize_keyboard=True)
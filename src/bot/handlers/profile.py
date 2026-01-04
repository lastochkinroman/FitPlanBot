"""Хэндлеры для команд профиля пользователя"""

from aiogram import F, Router, types
from aiogram.filters import Command

from src.bot.handlers.menu import format_user_profile, get_user_with_profile
from src.bot.keyboards.main_menu import get_main_menu_kb

router = Router()


@router.message(Command("profile"))
@router.message(F.text == "👤 Мой профиль")
async def profile_command(message: types.Message):
    """
    Обработчик команды /profile и кнопки "👤 Мой профиль"

    Args:
        message: Сообщение от пользователя
    """
    user_id = message.from_user.id

    # Получаем информацию о пользователе и его профиле
    user, profile = await get_user_with_profile(user_id)

    if not user:
        await message.answer(
            "❌ Вы ещё не зарегистрированы. Нажмите /start для начала работы.",
            reply_markup=get_main_menu_kb(),
        )
        return

    # Форматируем информацию о профиле
    profile_text = await format_user_profile(user, profile)

    await message.answer(
        text=profile_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("me"))
async def me_command(message: types.Message):
    """
    Альтернативная команда для просмотра профиля (/me)

    Args:
        message: Сообщение от пользователя
    """
    await profile_command(message)


# Дополнительные команды для работы с профилем


@router.message(Command("stats"))
async def profile_stats(message: types.Message):
    """
    Показывает статистику профиля

    Args:
        message: Сообщение от пользователя
    """
    user_id = message.from_user.id
    user, profile = await get_user_with_profile(user_id)

    if not user:
        await message.answer(
            "❌ Вы ещё не зарегистрированы. Нажмите /start для начала работы.",
            reply_markup=get_main_menu_kb(),
        )
        return

    if not profile:
        await message.answer(
            "📊 <b>Статистика профиля</b>\n\n"
            "❌ Анкета не заполнена\n"
            "➡️ Заполните анкету, чтобы увидеть статистику",
            parse_mode="HTML",
            reply_markup=get_main_menu_kb(),
        )
        return

    # Подсчитываем заполненные поля
    all_fields = [
        ("age", profile.age, "возраст"),
        ("gender", profile.gender, "пол"),
        ("height_cm", profile.height_cm, "рост"),
        ("weight_kg", profile.weight_kg, "вес"),
        ("target_weight_kg", profile.target_weight_kg, "целевой вес"),
        ("goal", profile.goal, "цель"),
        ("lifestyle", profile.lifestyle, "образ жизни"),
        ("sleep_hours", profile.sleep_hours, "часы сна"),
        ("is_experienced_training", profile.is_experienced_training, "опыт тренировок"),
        ("training_focus_area", profile.training_focus_area, "фокус тренировок"),
        ("training_location", profile.training_location, "место тренировок"),
        ("training_time_minutes", profile.training_time_minutes, "время тренировок"),
        ("training_days_per_week", profile.training_days_per_week, "дни тренировок"),
        ("preferred_training_type", profile.preferred_training_type, "тип тренировок"),
        ("preferred_difficulty", profile.preferred_difficulty, "сложность"),
        ("flexibility_level", profile.flexibility_level, "гибкость"),
        ("endurance_level", profile.endurance_level, "выносливость"),
    ]

    filled_fields = [
        name for field_name, value, name in all_fields if value is not None
    ]
    filled_count = len(filled_fields)
    total_fields = len(all_fields)
    completion_percentage = (
        int((filled_count / total_fields) * 100) if total_fields > 0 else 0
    )

    # Формируем сообщение
    stats_text = (
        f"📊 <b>Статистика профиля</b>\n\n"
        f"✅ <b>Заполнено:</b> {filled_count} из {total_fields} полей\n"
        f"📈 <b>Завершенность:</b> {completion_percentage}%\n\n"
    )

    if filled_fields:
        stats_text += "<b>Заполненные поля:</b>\n"
        for i, field_name in enumerate(filled_fields[:10], 1):  # Показываем первые 10
            stats_text += f"{i}. {field_name}\n"

        if len(filled_fields) > 10:
            stats_text += f"... и еще {len(filled_fields) - 10} полей\n"
    else:
        stats_text += "<i>Нет заполненных полей</i>\n"

    stats_text += (
        f"\n<b>Дата создания:</b> {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>Последнее обновление:</b> {profile.updated_at.strftime('%d.%m.%Y %H:%M') if profile.updated_at else 'Не обновлялось'}"
    )

    await message.answer(
        text=stats_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("reset_profile"))
async def reset_profile_command(message: types.Message):
    """
    Команда для сброса анкеты (заглушка)

    Args:
        message: Сообщение от пользователя
    """
    await message.answer(
        "🔄 <b>Сброс анкеты</b>\n\n"
        "⚠️ <i>Эта функция находится в разработке.</i>\n\n"
        "В будущем здесь можно будет сбросить заполненную анкету "
        "и начать заполнение заново.",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )

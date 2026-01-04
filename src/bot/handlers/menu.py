"""Хэндлеры для главного меню бота"""

from aiogram import F, Router, types
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.bot.dialogs.questionnaire.states import QuestionnaireStates
from src.bot.keyboards.main_menu import get_main_menu_kb
from src.database.models import User, UserProfile
from src.database.session import async_session_maker

router = Router()

# Константы для отображения
GENDER_DISPLAY_MAP = {
    "male": "👨 Мужской",
    "female": "👩 Женский",
    "other": "🏳️‍🌈 Другой",
}

GOAL_DISPLAY_MAP = {
    "lose_weight": "⚖️ Похудеть",
    "gain_muscle": "💪 Набрать мышечную массу",
    "maintain": "🛡️ Поддерживать форму",
    "improve_health": "❤️ Улучшить здоровье",
    "improve_endurance": "🏃 Увеличить выносливость",
    "body_recomposition": "🎨 Преобразить тело",
}


async def get_user_with_profile(telegram_id: int):
    """
    Получает пользователя и его профиль из базы данных

    Args:
        telegram_id: ID пользователя в Telegram

    Returns:
        tuple: (user, profile) или (None, None) если пользователь не найден
    """
    async with async_session_maker() as session:
        stmt = (
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.profile))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return None, None

        return user, user.profile


async def format_user_profile(user: User, profile: UserProfile | None) -> str:
    """
    Форматирует информацию о профиле пользователя для отображения

    Args:
        user: Объект пользователя
        profile: Объект профиля или None

    Returns:
        str: Отформатированный текст профиля
    """
    # Базовая информация о пользователе
    base_info = [
        f"👤 <b>Пользователь:</b> {user.first_name} {user.last_name or ''}",
        f"📱 <b>Username:</b> @{user.telegram_username or 'не указан'}",
        f"🆔 <b>Telegram ID:</b> {user.telegram_id}",
        f"📅 <b>Зарегистрирован:</b> {user.created_at.strftime('%d.%m.%Y %H:%M')}",
    ]

    if not profile:
        return (
            "📋 <b>Ваш профиль</b>\n\n"
            + "\n".join(base_info)
            + "\n\n📝 <b>Анкета:</b> ❌ Не заполнена\n\n"
            "➡️ <i>Заполните анкету, чтобы получить персональный план!</i>"
        )

    # Информация о заполнении анкеты
    completed_status = "✅ Заполнена" if profile.profile_completed else "⏳ В процессе"
    completed_date = (
        profile.completed_at.strftime("%d.%m.%Y %H:%M")
        if profile.completed_at
        else "Не завершена"
    )

    # Основные данные профиля
    profile_fields = []

    if profile.age:
        profile_fields.append(f"• <b>Возраст:</b> {profile.age} лет")
    if profile.gender:
        display_gender = GENDER_DISPLAY_MAP.get(profile.gender, f"👤 {profile.gender}")
        profile_fields.append(f"• <b>Пол:</b> {display_gender}")
    if profile.height_cm:
        profile_fields.append(f"• <b>Рост:</b> {profile.height_cm} см")
    if profile.weight_kg:
        profile_fields.append(f"• <b>Вес:</b> {profile.weight_kg} кг")
    if profile.target_weight_kg:
        profile_fields.append(f"• <b>Целевой вес:</b> {profile.target_weight_kg} кг")
    if profile.goal:
        display_goal = GOAL_DISPLAY_MAP.get(profile.goal, profile.goal)
        profile_fields.append(f"• <b>Цель:</b> {display_goal}")

    profile_details = (
        "\n".join(profile_fields)
        if profile_fields
        else "<i>Основные данные не заполнены</i>"
    )

    # Подсчет заполненных полей
    filled_fields = [
        profile.age,
        profile.gender,
        profile.height_cm,
        profile.weight_kg,
        profile.goal,
    ]
    filled_count = sum(1 for field in filled_fields if field is not None)

    return (
        "📋 <b>Ваш профиль</b>\n\n"
        + "\n".join(base_info)
        + f"\n\n📝 <b>Анкета:</b> {completed_status}\n"
        f"📅 <b>Завершена:</b> {completed_date}\n\n"
        "<b>Основные данные:</b>\n"
        + profile_details
        + f"\n\n➡️ <i>Анкета заполнена на {filled_count}/5 основных параметров</i>"
    )


@router.message(F.text == "📝 Заполнить анкету")
async def start_questionnaire(message: types.Message, dialog_manager: DialogManager):
    """
    Запуск диалога заполнения анкеты

    Args:
        message: Сообщение от пользователя
        dialog_manager: Менеджер диалогов
    """
    await dialog_manager.start(QuestionnaireStates.age, mode=StartMode.RESET_STACK)


@router.message(F.text == "👤 Мой профиль")
async def show_user_profile(message: types.Message):
    """
    Показывает профиль пользователя

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

    profile_text = await format_user_profile(user, profile)
    await message.answer(
        text=profile_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: types.Message):
    """
    Показывает меню настроек

    Args:
        message: Сообщение от пользователя
    """
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Здесь можно будет настроить:\n"
        "• Время уведомлений\n"
        "• Частоту тренировок\n"
        "• Предпочтения по питанию\n\n"
        "<i>Функционал настроек находится в разработке...</i>",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )


@router.message(F.text == "💳 Купить подписку")
async def buy_subscription(message: types.Message):
    """
    Обработка запроса на покупку подписки

    Args:
        message: Сообщение от пользователя
    """
    from src.database.repositories.subscription_repo import SubscriptionRepository
    from src.database.repositories.user_repo import UserRepository

    telegram_id = message.from_user.id

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(telegram_id)

        if not user:
            await message.answer(
                "❌ <b>Пользователь не найден</b>\n\n"
                "Сначала зарегистрируйтесь с помощью /start",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb(),
            )
            return

        repo = SubscriptionRepository(session)
        subscription = await repo.create_pending(user.id)

        if subscription:
            await message.answer(
                "💳 <b>Заявка на подписку отправлена!</b>\n\n"
                f"📅 <b>Статус:</b> Ожидает подтверждения\n"
                f"🆔 <b>ID заявки:</b> {subscription.id[:8]}...\n\n"
                "Администратор рассмотрит вашу заявку и активирует подписку.\n"
                "После активации вы получите доступ ко всем функциям бота:\n"
                "✅ Персональные планы тренировок\n"
                "✅ Индивидуальное питание\n"
                "✅ Ежедневные уведомления\n"
                "✅ Отслеживание прогресса\n\n"
                "<i>Обычно активация занимает не более 24 часов.</i>",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb(),
            )
        else:
            await message.answer(
                "❌ <b>Ошибка при создании заявки</b>\n\n"
                "Попробуйте позже или свяжитесь с поддержкой.",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb(),
            )


# Дополнительный хэндлер для кнопки "🏋️ Мой план" (заглушка)
@router.message(F.text == "🏋️ Мой план")
async def show_workout_plan(message: types.Message):
    """
    Показывает план тренировок пользователя

    Args:
        message: Сообщение от пользователя
    """
    await message.answer(
        "🏋️ <b>Ваш план тренировок</b>\n\n"
        "<i>Функционал подбора плана тренировок находится в разработке...</i>\n\n"
        "После заполнения анкеты и активации подписки здесь появится "
        "персональный план тренировок, подобранный специально для вас.",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )


# Дополнительный хэндлер для кнопки "🍎 Питание" (заглушка)
@router.message(F.text == "🍎 Питание")
async def show_nutrition_plan(message: types.Message):
    """
    Показывает план питания пользователя

    Args:
        message: Сообщение от пользователя
    """
    await message.answer(
        "🍎 <b>Ваш план питания</b>\n\n"
        "<i>Функционал подбора плана питания находится в разработке...</i>\n\n"
        "После заполнения анкеты и активации подписки здесь появится "
        "персональный план питания, подобранный специально для вас.",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )


__all__ = ["get_user_with_profile", "format_user_profile"]

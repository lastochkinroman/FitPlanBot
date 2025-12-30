from aiogram import Router, types, F
from aiogram_dialog import DialogManager
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.session import async_session_maker
from src.database.models import User, UserProfile
from src.bot.keyboards.main_menu import get_main_menu_kb

from aiogram_dialog import DialogManager, StartMode
from src.bot.dialogs.questionnaire.states import QuestionnaireStates

router = Router()
@router.message(F.text == "📝 Заполнить анкету")
async def start_questionnaire(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        QuestionnaireStates.age,
        mode=StartMode.RESET_STACK
    )

async def get_profile_info(user_id: int):
    """
    Получает информацию о профиле пользователя
    Возвращает (user, profile)
    """
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == user_id).options(
            selectinload(User.profile)
        )
        result = await session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None, None
        
        profile = db_user.profile
        return db_user, profile

async def show_profile(user_id: int, first_name: str):
    """
    Формирует текст профиля для показа
    """
    db_user, profile = await get_profile_info(user_id)
    
    if not db_user:
        return "❌ Вы ещё не зарегистрированы. Нажмите /start для начала работы."
    
    if not profile:
        return (
            "📋 <b>Ваш профиль</b>\n\n"
            f"👤 <b>Пользователь:</b> {db_user.first_name} {db_user.last_name or ''}\n"
            f"📱 <b>Username:</b> @{db_user.telegram_username or 'не указан'}\n"
            f"🆔 <b>Telegram ID:</b> {db_user.telegram_id}\n"
            f"📅 <b>Зарегистрирован:</b> {db_user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            "📝 <b>Анкета:</b> ❌ Не заполнена\n\n"
            "➡️ <i>Заполните анкету, чтобы получить персональный план!</i>"
        )
    else:
        # Формируем информацию о профиле
        profile_info = []
        if profile.age:
            profile_info.append(f"• <b>Возраст:</b> {profile.age} лет")
        if profile.gender:
            gender_display = {
                "male": "👨 Мужской",
                "female": "👩 Женский",
                "other": "⚧️ Другой"
            }.get(profile.gender, f"👤 {profile.gender}")
            profile_info.append(f"• <b>Пол:</b> {gender_display}")
        if profile.height_cm:
            profile_info.append(f"• <b>Рост:</b> {profile.height_cm} см")
        if profile.weight_kg:
            profile_info.append(f"• <b>Вес:</b> {profile.weight_kg} кг")
        if profile.target_weight_kg:
            profile_info.append(f"• <b>Целевой вес:</b> {profile.target_weight_kg} кг")
        if profile.goal:
            goal_display = {
                "lose_weight": "⚖️ Похудеть",
                "gain_muscle": "💪 Набрать мышечную массу",
                "maintain": "🛡️ Поддерживать форму",
                "improve_health": "❤️ Улучшить здоровье",
                "improve_endurance": "🏃 Увеличить выносливость",
                "body_recomposition": "🎨 Преобразить тело"
            }.get(profile.goal, profile.goal)
            profile_info.append(f"• <b>Цель:</b> {goal_display}")
        
        profile_details = "\n".join(profile_info) if profile_info else "<i>Основные данные не заполнены</i>"
        
        completed_status = "✅ Заполнена" if profile.profile_completed else "⏳ В процессе"
        completed_date = profile.completed_at.strftime('%d.%m.%Y %H:%M') if profile.completed_at else 'Не завершена'
        
        return (
            "📋 <b>Ваш профиль</b>\n\n"
            f"👤 <b>Пользователь:</b> {db_user.first_name} {db_user.last_name or ''}\n"
            f"📱 <b>Username:</b> @{db_user.telegram_username or 'не указан'}\n"
            f"🆔 <b>Telegram ID:</b> {db_user.telegram_id}\n"
            f"📅 <b>Зарегистрирован:</b> {db_user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📝 <b>Анкета:</b> {completed_status}\n"
            f"📅 <b>Завершена:</b> {completed_date}\n\n"
            "<b>Основные данные:</b>\n"
            f"{profile_details}\n\n"
            f"➡️ <i>Анкета заполнена на {len([p for p in [profile.age, profile.gender, profile.height_cm, profile.weight_kg, profile.goal] if p])}/5 основных параметров</i>"
        )

# Хэндлер для кнопки "👤 Мой профиль"
@router.message(F.text == "👤 Мой профиль")
async def profile_menu_button(message: types.Message):
    profile_text = await show_profile(message.from_user.id, message.from_user.first_name)
    await message.answer(
        text=profile_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )

# Остальные хэндлеры для других кнопок остаются без изменений

@router.message(F.text == "🏋️ Мой план")
async def show_workout_plan(message: types.Message):
    await message.answer(
        "🏋️ <b>План тренировок</b>\n\n"
        "Чтобы получить персонализированный план, нужно:\n"
        "1️⃣ Заполнить анкету\n"
        "2️⃣ Активировать подписку\n\n"
        "<i>Функционал тренировок находится в разработке...</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "🍎 Питание")
async def show_nutrition_plan(message: types.Message):
    await message.answer(
        "🍎 <b>План питания</b>\n\n"
        "Индивидуальный рацион будет доступен после:\n"
        "1️⃣ Заполнения анкеты\n"
        "2️⃣ Активации подписки\n\n"
        "<i>Функционал питания находится в разработке...</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: types.Message):
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Здесь можно будет настроить:\n"
        "• Время уведомлений\n"
        "• Частоту тренировок\n"
        "• Предпочтения по питанию\n\n"
        "<i>Функционал настроек находится в разработке...</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "💳 Купить подписку")
async def show_subscription(message: types.Message):
    await message.answer(
        "💳 <b>Подписка</b>\n\n"
        "Полный доступ к функциям бота:\n"
        "✅ Персональные планы тренировок\n"
        "✅ Индивидуальное питание\n"
        "✅ Ежедневные уведомления\n"
        "✅ Отслеживание прогресса\n\n"
        "<i>Система оплаты находится в разработке...</i>\n"
        "Для активации подписки свяжитесь с администратором.",
        parse_mode="HTML"
    )

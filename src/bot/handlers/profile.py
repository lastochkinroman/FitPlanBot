from aiogram import Router, types, F
from aiogram.filters import Command

from src.bot.handlers.menu import show_profile
from src.bot.keyboards.main_menu import get_main_menu_kb

router = Router()

@router.message(Command("profile"))
async def profile_command(message: types.Message):
    profile_text = await show_profile(message.from_user.id, message.from_user.first_name)
    await message.answer(
        text=profile_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
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

@router.message(Command("profile"))
async def profile_command(message: types.Message):
    user = message.from_user
    telegram_id = user.id
    
    db_user, profile = await get_profile_info(telegram_id)
    
    if not db_user:
        await message.answer(
            "❌ Вы ещё не зарегистрированы. Нажмите /start для начала работы.",
            reply_markup=get_main_menu_kb()
        )
        return
    
    if not profile:
        profile_text = (
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
            gender_emoji = {"male": "👨", "female": "👩", "other": "⚧️"}.get(profile.gender, "👤")
            profile_info.append(f"• <b>Пол:</b> {gender_emoji} {profile.gender}")
        if profile.height_cm:
            profile_info.append(f"• <b>Рост:</b> {profile.height_cm} см")
        if profile.weight_kg:
            profile_info.append(f"• <b>Вес:</b> {profile.weight_kg} кг")
        if profile.target_weight_kg:
            profile_info.append(f"• <b>Целевой вес:</b> {profile.target_weight_kg} кг")
        if profile.goal:
            profile_info.append(f"• <b>Цель:</b> {profile.goal}")
        
        profile_details = "\n".join(profile_info) if profile_info else "<i>Основные данные не заполнены</i>"
        
        completed_status = "✅ Заполнена" if profile.profile_completed else "⏳ В процессе"
        completed_date = profile.completed_at.strftime('%d.%m.%Y %H:%M') if profile.completed_at else 'Не завершена'
        
        profile_text = (
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
    
    await message.answer(
        text=profile_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )


# Хэндлер для кнопки "👤 Мой профиль" из меню
@router.message(F.text == "👤 Мой профиль")
async def profile_menu_button(message: types.Message):
    await profile_command(message)
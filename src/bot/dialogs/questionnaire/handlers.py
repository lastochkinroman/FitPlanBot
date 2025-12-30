from typing import Any
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select

from src.utils.validators import validate_age, validate_height, validate_weight
from src.database.session import async_session_maker
from src.database.models import User, UserProfile


async def on_age_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    # Валидация возраста
    is_valid, age = validate_age(text)
    
    if not is_valid:
        await message.answer(
            "❌ Возраст должен быть числом от 14 до 100.\n"
            "Пожалуйста, введите корректный возраст:"
        )
        return
    
    # Сохраняем возраст в данные диалога
    dialog_manager.dialog_data["age"] = age
    
    # Переходим к следующему состоянию (пол)
    await dialog_manager.next()


async def on_gender_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str  # Это будет значение из items, а не отображаемый текст
):
    # item_id - это значение, которое мы передали в Radio
    # В Radio items должен быть список ТУПЛОВ или словарей, а не просто строк
    
    # Преобразуем в значение для БД
    gender_map = {
        "male": "male",
        "female": "female",
        "other": "other"
    }
    
    gender = gender_map.get(item_id, "male")  # По умолчанию male
    dialog_manager.dialog_data["gender"] = gender
    
    await callback.answer(f"Выбран пол: {gender}")
    await dialog_manager.next()


async def on_height_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    # Валидация роста
    is_valid, height = validate_height(text)
    
    if not is_valid:
        await message.answer(
            "❌ Рост должен быть числом от 100 до 250 см.\n"
            "Пожалуйста, введите корректный рост:"
        )
        return
    
    dialog_manager.dialog_data["height_cm"] = height
    await dialog_manager.next()


async def on_weight_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    # Валидация веса
    is_valid, weight = validate_weight(text)
    
    if not is_valid:
        await message.answer(
            "❌ Вес должен быть числом от 30 до 300 кг.\n"
            "Пожалуйста, введите корректный вес (можно с десятичной точкой):"
        )
        return
    
    dialog_manager.dialog_data["weight_kg"] = weight
    await dialog_manager.next()


async def on_target_weight_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    # Валидация целевого веса (аналогично текущему весу)
    is_valid, weight = validate_weight(text)
    
    if not is_valid:
        await message.answer(
            "❌ Вес должен быть числом от 30 до 300 кг.\n"
            "Пожалуйста, введите корректный вес:"
        )
        return
    
    dialog_manager.dialog_data["target_weight_kg"] = weight
    await dialog_manager.next()


async def on_body_type_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str  # Исправляем: должно быть item_id, как в on_gender_selected
):
    # Сохраняем тип телосложения
    body_type_map = {
        "📐 Эктоморф (худощавый)": "ectomorph",
        "📦 Мезоморф (мускулистый)": "mesomorph",
        "📦 Эндоморф (склонный к полноте)": "endomorph",
        "❓ Не знаю": "unknown"
    }
    
    body_type = body_type_map.get(item_id, "unknown")
    dialog_manager.dialog_data["body_type"] = body_type
    
    await callback.answer("Данные сохранены!")
    await dialog_manager.next()


async def get_summary_data(dialog_manager: DialogManager, **kwargs):
    """Готовит данные для отображения в окне подтверждения"""
    data = dialog_manager.dialog_data
    
    # Форматируем данные для отображения
    summary = []
    
    if "age" in data:
        summary.append(["Возраст", f"{data['age']} лет"])
    
    if "gender" in data:
        gender_display = {"male": "👨 Мужской", "female": "👩 Женский"}.get(data["gender"], data["gender"])
        summary.append(["Пол", gender_display])
    
    if "height_cm" in data:
        summary.append(["Рост", f"{data['height_cm']} см"])
    
    if "weight_kg" in data:
        summary.append(["Вес", f"{data['weight_kg']} кг"])
    
    if "target_weight_kg" in data:
        summary.append(["Целевой вес", f"{data['target_weight_kg']} кг"])
    
    if "body_type" in data:
        body_type_display = {
            "ectomorph": "📐 Эктоморф",
            "mesomorph": "📦 Мезоморф", 
            "endomorph": "📦 Эндоморф",
            "unknown": "❓ Не знаю"
        }.get(data["body_type"], data["body_type"])
        summary.append(["Тип телосложения", body_type_display])
    
    return {"summary_items": summary}


async def on_confirmation_save(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
):
    """Сохранение анкеты в БД"""
    user_id = callback.from_user.id
    data = dialog_manager.dialog_data
    
    # Добавляем обязательные поля по умолчанию
    defaults = {
        "is_experienced_training": False,  # Значение по умолчанию
        "goal": "unknown",
        "lifestyle": "unknown",
        "training_days_per_week": 0,
        "sleep_hours": 0,
    }
    
    # Объединяем данные с дефолтами
    data_with_defaults = {**defaults, **data}
    
    async with async_session_maker() as session:
        # Находим пользователя
        stmt_user = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt_user)
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("❌ Пользователь не найден!")
            return
        
        # Проверяем, есть ли уже профиль
        stmt_profile = select(UserProfile).where(UserProfile.user_id == user.id)
        result = await session.execute(stmt_profile)
        profile = result.scalar_one_or_none()
        
        if profile:
            # Обновляем существующий профиль
            for key, value in data_with_defaults.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
        else:
            # Создаём новый профиль
            profile = UserProfile(
                user_id=user.id,
                **{k: v for k, v in data_with_defaults.items() if hasattr(UserProfile, k)}
            )
            session.add(profile)
        
        # Устанавливаем флаг завершения
        profile.profile_completed = True
        profile.completed_at = datetime.utcnow()
        
        try:
            await session.commit()
            await callback.answer("✅ Анкета сохранена!")
            
            # Завершаем диалог
            await dialog_manager.done()
            
            # Показываем сообщение об успешном сохранении
            await callback.message.answer(
                "🎉 <b>Анкета успешно сохранена!</b>\n\n"
                "Теперь вы можете получить персонализированный план тренировок и питания.\n\n"
                "Нажмите <b>🏋️ Мой план</b> для получения тренировочного плана.",
                parse_mode="HTML"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error saving profile: {e}")
            await callback.answer("❌ Ошибка при сохранении анкеты!")

async def on_confirmation_edit(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
):
    """Возврат к редактированию анкеты"""
    from .states import QuestionnaireStates  # Локальный импорт
    await dialog_manager.switch_to(QuestionnaireStates.age)


async def getter_summary(dialog_manager: DialogManager, **kwargs):
    return await get_summary_data(dialog_manager, **kwargs)
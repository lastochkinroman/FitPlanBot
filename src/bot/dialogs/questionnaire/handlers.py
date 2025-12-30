from typing import Any
from datetime import datetime
import logging
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select

logger = logging.getLogger(__name__)

from src.utils.validators import (
    validate_age, validate_height, validate_weight, validate_sleep_hours,
    validate_training_time, validate_training_days, validate_date
)
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


# Группа 2: Цели и образ жизни

async def on_goal_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["goal"] = item_id
    await callback.answer("Цель выбрана!")
    await dialog_manager.next()


async def on_lifestyle_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["lifestyle"] = item_id
    await callback.answer("Образ жизни выбран!")
    await dialog_manager.next()


async def on_sleep_hours_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    is_valid, hours = validate_sleep_hours(text)

    if not is_valid:
        await message.answer(
            "❌ Количество часов сна должно быть числом от 4.0 до 12.0.\n"
            "Пожалуйста, введите корректное значение:"
        )
        return

    dialog_manager.dialog_data["sleep_hours"] = hours
    await dialog_manager.next()


async def on_genetics_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    dialog_manager.dialog_data["genetics_description"] = text.strip() or ""
    await dialog_manager.next()


async def on_experience_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    # item_id приходит как строка "True" или "False" из callback data
    dialog_manager.dialog_data["is_experienced_training"] = item_id == "True"
    await callback.answer("Опыт сохранён!")
    await dialog_manager.next()


async def on_last_form_date_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    text = text.strip().lower()
    if text in ["никогда", "never", "н"]:
        dialog_manager.dialog_data["last_ideal_form_date"] = None
    else:
        is_valid, date_obj = validate_date(text)
        if not is_valid:
            await message.answer(
                "❌ Дата должна быть в формате ДД.ММ.ГГГГ\n"
                "Или напишите 'никогда'\n"
                "Пример: 01.01.2020"
            )
            return
        dialog_manager.dialog_data["last_ideal_form_date"] = date_obj
    await dialog_manager.next()


# Группа 3: Тренировки

async def on_training_focus_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["training_focus_area"] = item_id
    await callback.answer("Фокус выбран!")
    await dialog_manager.next()


async def on_training_location_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["training_location"] = item_id
    await callback.answer("Место выбрано!")
    await dialog_manager.next()


async def on_training_time_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    is_valid, minutes = validate_training_time(text)

    if not is_valid:
        await message.answer(
            "❌ Время тренировки должно быть числом от 30 до 120 минут.\n"
            "Пожалуйста, введите корректное значение:"
        )
        return

    dialog_manager.dialog_data["training_time_minutes"] = minutes
    await dialog_manager.next()


async def on_training_days_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    is_valid, days = validate_training_days(text)

    if not is_valid:
        await message.answer(
            "❌ Количество дней должно быть числом от 1 до 7.\n"
            "Пожалуйста, введите корректное значение:"
        )
        return

    dialog_manager.dialog_data["training_days_per_week"] = days
    await dialog_manager.next()


async def on_training_type_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["preferred_training_type"] = item_id
    await callback.answer("Тип тренировок выбран!")
    await dialog_manager.next()


async def on_training_difficulty_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["preferred_difficulty"] = item_id
    await callback.answer("Сложность выбрана!")
    await dialog_manager.next()


# Группа 4: Здоровье

async def on_injuries_selected(
    message: MessageInput,
    widget: Any,
    dialog_manager: DialogManager,
    text: str
):
    dialog_manager.dialog_data["injuries_description"] = text.strip() or ""
    await dialog_manager.next()


async def on_flexibility_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["flexibility_level"] = item_id
    await callback.answer("Гибкость оценена!")
    await dialog_manager.next()


async def on_endurance_selected(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str
):
    dialog_manager.dialog_data["endurance_level"] = item_id
    await callback.answer("Выносливость оценена!")
    await dialog_manager.next()


async def get_summary_data(dialog_manager: DialogManager, **kwargs):
    """Готовит данные для отображения в окне подтверждения"""
    data = dialog_manager.dialog_data

    # Форматируем данные для отображения
    summary = []

    # Группа 1: Основные данные
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

    # Группа 2: Цели и образ жизни
    if "goal" in data:
        goal_display = {
            "lose_weight": "⚖️ Похудеть",
            "gain_muscle": "💪 Набрать массу",
            "maintain": "🛡️ Поддерживать",
            "improve_health": "❤️ Здоровье",
            "improve_endurance": "🏃 Выносливость",
            "body_recomposition": "🎨 Преобразить тело"
        }.get(data["goal"], data["goal"])
        summary.append(["Цель", goal_display])

    if "lifestyle" in data:
        lifestyle_display = {
            "sedentary": "🪑 Сидячий",
            "lightly_active": "🚶 Легкая активность",
            "moderately_active": "🏃 Средняя активность",
            "very_active": "💪 Высокая активность",
            "extremely_active": "🏆 Экстремальная активность"
        }.get(data["lifestyle"], data["lifestyle"])
        summary.append(["Образ жизни", lifestyle_display])

    if "sleep_hours" in data:
        summary.append(["Часы сна", f"{data['sleep_hours']} ч"])

    if "genetics_description" in data and data["genetics_description"]:
        summary.append(["Генетика", data["genetics_description"][:50] + ("..." if len(data["genetics_description"]) > 50 else "")])

    if "is_experienced_training" in data:
        exp_display = "✅ Есть опыт" if data["is_experienced_training"] else "❌ Нет опыта"
        summary.append(["Опыт тренировок", exp_display])

    if "last_ideal_form_date" in data:
        if data["last_ideal_form_date"]:
            # data["last_ideal_form_date"] - это datetime.date объект
            date_str = data["last_ideal_form_date"].strftime("%d.%m.%Y")
            summary.append(["Последняя идеальная форма", date_str])
        else:
            summary.append(["Последняя идеальная форма", "Никогда"])

    # Группа 3: Тренировки
    if "training_focus_area" in data:
        focus_display = {
            "full_body": "💪 Всё тело",
            "upper_body": "🏋️ Верхняя часть",
            "lower_body": "🦵 Нижняя часть",
            "glutes_legs": "🍖 Ягодицы и ноги",
            "arms_shoulders": "🦾 Руки и плечи",
            "core": "🔥 Корпус",
            "unsure": "❓ Не уверен"
        }.get(data["training_focus_area"], data["training_focus_area"])
        summary.append(["Фокус тренировок", focus_display])

    if "training_location" in data:
        location_display = {
            "gym": "🏋️ Зал",
            "home": "🏠 Дом",
            "outdoor": "🌳 Улица",
            "online": "💻 Онлайн",
            "other": "❓ Другое"
        }.get(data["training_location"], data["training_location"])
        summary.append(["Место тренировок", location_display])

    if "training_time_minutes" in data:
        summary.append(["Время тренировки", f"{data['training_time_minutes']} мин"])

    if "training_days_per_week" in data:
        summary.append(["Дней в неделю", f"{data['training_days_per_week']} дней"])

    if "preferred_training_type" in data:
        type_display = {
            "strength": "🏋️ Силовые",
            "cardio": "🏃 Кардио",
            "yoga_pilates": "🤸 Йога/пилатес",
            "combat": "🥊 Боевые искусства",
            "swimming": "🏊 Плавание",
            "cycling": "🚴 Велоспорт",
            "unsure": "❓ Не знаю"
        }.get(data["preferred_training_type"], data["preferred_training_type"])
        summary.append(["Тип тренировок", type_display])

    if "preferred_difficulty" in data:
        diff_display = {
            "beginner": "🟢 Начальный",
            "intermediate": "🟡 Средний",
            "advanced": "🔴 Продвинутый",
            "expert": "⚫ Профессиональный"
        }.get(data["preferred_difficulty"], data["preferred_difficulty"])
        summary.append(["Сложность", diff_display])

    # Группа 4: Здоровье
    if "injuries_description" in data and data["injuries_description"]:
        summary.append(["Травмы/ограничения", data["injuries_description"][:50] + ("..." if len(data["injuries_description"]) > 50 else "")])

    if "flexibility_level" in data:
        flex_display = {
            "excellent": "🟢 Отличная",
            "good": "🟡 Хорошая",
            "average": "🟠 Средняя",
            "poor": "🔴 Плохая",
            "very_poor": "⚫ Очень плохая"
        }.get(data["flexibility_level"], data["flexibility_level"])
        summary.append(["Гибкость", flex_display])

    if "endurance_level" in data:
        end_display = {
            "excellent": "🟢 Отличная",
            "good": "🟡 Хорошая",
            "average": "🟠 Средняя",
            "poor": "🔴 Плохая",
            "very_poor": "⚫ Очень плохая"
        }.get(data["endurance_level"], data["endurance_level"])
        summary.append(["Выносливость", end_display])

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
            logger.info(f"Profile saved successfully for user {user_id}")
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
            logger.error(f"Error saving profile for user {user_id}: {e}")
            logger.error(f"Data being saved: {data_with_defaults}")
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

"""Обработчики для диалога анкеты пользователя"""

import logging
from datetime import datetime
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import select

from src.database.models import User, UserProfile
from src.database.session import async_session_maker
from src.utils.validators import (
    validate_age,
    validate_date,
    validate_height,
    validate_sleep_hours,
    validate_training_days,
    validate_training_time,
    validate_weight,
)

logger = logging.getLogger(__name__)

# Константы для маппинга значений
GENDER_MAP = {"male": "male", "female": "female", "other": "other"}

BODY_TYPE_MAP = {
    "📐 Эктоморф (худощавый)": "ectomorph",
    "📦 Мезоморф (мускулистый)": "mesomorph",
    "📦 Эндоморф (склонный к полноте)": "endomorph",
    "❓ Не знаю": "unknown",
}

GOAL_DISPLAY_MAP = {
    "lose_weight": "⚖️ Похудеть",
    "gain_muscle": "💪 Набрать массу",
    "maintain": "🛡️ Поддерживать",
    "improve_health": "❤️ Здоровье",
    "improve_endurance": "🏃 Выносливость",
    "body_recomposition": "🎨 Преобразить тело",
}

LIFESTYLE_DISPLAY_MAP = {
    "sedentary": "🪑 Сидячий",
    "lightly_active": "🚶 Легкая активность",
    "moderately_active": "🏃 Средняя активность",
    "very_active": "💪 Высокая активность",
    "extremely_active": "🏆 Экстремальная активность",
}

FLEXIBILITY_DISPLAY_MAP = {
    "excellent": "🟢 Отличная",
    "good": "🟡 Хорошая",
    "average": "🟠 Средняя",
    "poor": "🔴 Плохая",
    "very_poor": "⚫ Очень плохая",
}

# Обработчики для группы 1: Основные данные


async def on_age_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода возраста"""
    try:
        is_valid, age = validate_age(text)

        if not is_valid:
            await message.answer(
                "❌ Возраст должен быть числом от 14 до 100.\n"
                "Пожалуйста, введите корректный возраст:"
            )
            return

        dialog_manager.dialog_data["age"] = age
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating age: {e}")
        await message.answer(
            "❌ Неверный формат возраста.\n" "Пожалуйста, введите число от 14 до 100:"
        )


async def on_gender_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора пола"""
    try:
        gender = GENDER_MAP.get(item_id, "male")
        dialog_manager.dialog_data["gender"] = gender

        gender_display = {
            "male": "👨 Мужской",
            "female": "👩 Женский",
            "other": "🏳️‍🌈 Другой",
        }.get(gender, gender)

        await callback.answer(f"Выбран пол: {gender_display}")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in gender selection: {e}")
        await callback.answer("❌ Ошибка при выборе пола")


async def on_height_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода роста"""
    try:
        is_valid, height = validate_height(text)

        if not is_valid:
            await message.answer(
                "❌ Рост должен быть числом от 100 до 250 см.\n"
                "Пожалуйста, введите корректный рост:"
            )
            return

        dialog_manager.dialog_data["height_cm"] = height
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating height: {e}")
        await message.answer(
            "❌ Неверный формат роста.\n" "Пожалуйста, введите число от 100 до 250 см:"
        )


async def on_weight_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода веса"""
    try:
        is_valid, weight = validate_weight(text)

        if not is_valid:
            await message.answer(
                "❌ Вес должен быть числом от 30 до 300 кг.\n"
                "Пожалуйста, введите корректный вес:"
            )
            return

        dialog_manager.dialog_data["weight_kg"] = float(weight)
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating weight: {e}")
        await message.answer(
            "❌ Неверный формат веса.\n" "Пожалуйста, введите число от 30 до 300 кг:"
        )


async def on_target_weight_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода целевого веса"""
    try:
        is_valid, weight = validate_weight(text)

        if not is_valid:
            await message.answer(
                "❌ Целевой вес должен быть числом от 30 до 300 кг.\n"
                "Пожалуйста, введите корректное значение:"
            )
            return

        dialog_manager.dialog_data["target_weight_kg"] = float(weight)
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating target weight: {e}")
        await message.answer(
            "❌ Неверный формат веса.\n" "Пожалуйста, введите число от 30 до 300 кг:"
        )


async def on_body_type_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора типа телосложения"""
    try:
        body_type = BODY_TYPE_MAP.get(item_id, "unknown")
        dialog_manager.dialog_data["body_type"] = body_type
        await callback.answer("✅ Тип телосложения сохранен!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in body type selection: {e}")
        await callback.answer("❌ Ошибка при выборе типа телосложения")


# Обработчики для группы 2: Цели и образ жизни


async def on_goal_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора цели"""
    try:
        dialog_manager.dialog_data["goal"] = item_id
        display_name = GOAL_DISPLAY_MAP.get(item_id, item_id)
        await callback.answer(f"✅ Цель '{display_name}' выбрана!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in goal selection: {e}")
        await callback.answer("❌ Ошибка при выборе цели")


async def on_lifestyle_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора образа жизни"""
    try:
        dialog_manager.dialog_data["lifestyle"] = item_id
        display_name = LIFESTYLE_DISPLAY_MAP.get(item_id, item_id)
        await callback.answer(f"✅ Образ жизни '{display_name}' выбран!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in lifestyle selection: {e}")
        await callback.answer("❌ Ошибка при выборе образа жизни")


async def on_sleep_hours_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода часов сна"""
    try:
        is_valid, hours = validate_sleep_hours(text)

        if not is_valid:
            await message.answer(
                "❌ Количество часов сна должно быть числом от 4.0 до 12.0.\n"
                "Пожалуйста, введите корректное значение:"
            )
            return

        dialog_manager.dialog_data["sleep_hours"] = float(hours)
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating sleep hours: {e}")
        await message.answer(
            "❌ Неверный формат.\n" "Пожалуйста, введите число от 4.0 до 12.0 часов:"
        )


async def on_genetics_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода описания генетики"""
    try:
        description = text.strip()
        dialog_manager.dialog_data["genetics_description"] = (
            description if description else None
        )
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in genetics input: {e}")
        await message.answer("❌ Ошибка при сохранении описания")


async def on_experience_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора опыта тренировок"""
    try:
        has_experience = item_id == "True"
        dialog_manager.dialog_data["is_experienced_training"] = has_experience

        experience_text = "есть опыт" if has_experience else "нет опыта"
        await callback.answer(f"✅ Опыт тренировок: {experience_text}")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in experience selection: {e}")
        await callback.answer("❌ Ошибка при выборе опыта")


async def on_last_form_date_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода даты последней идеальной формы"""
    try:
        text = text.strip().lower()

        if text in ["никогда", "never", "н", "нет"]:
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

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating date: {e}")
        await message.answer(
            "❌ Неверный формат даты.\n"
            "Используйте формат ДД.ММ.ГГГГ или напишите 'никогда':"
        )


# Обработчики для группы 3: Тренировки


async def on_training_focus_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора фокуса тренировок"""
    try:
        dialog_manager.dialog_data["training_focus_area"] = item_id
        await callback.answer("✅ Фокус тренировок сохранен!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in training focus selection: {e}")
        await callback.answer("❌ Ошибка при выборе фокуса")


async def on_training_location_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора места тренировок"""
    try:
        dialog_manager.dialog_data["training_location"] = item_id
        await callback.answer("✅ Место тренировок сохранено!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in training location selection: {e}")
        await callback.answer("❌ Ошибка при выборе места")


async def on_training_time_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода времени тренировки"""
    try:
        is_valid, minutes = validate_training_time(text)

        if not is_valid:
            await message.answer(
                "❌ Время тренировки должно быть числом от 30 до 120 минут.\n"
                "Пожалуйста, введите корректное значение:"
            )
            return

        dialog_manager.dialog_data["training_time_minutes"] = minutes
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating training time: {e}")
        await message.answer(
            "❌ Неверный формат.\n" "Пожалуйста, введите число от 30 до 120 минут:"
        )


async def on_training_days_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода дней тренировок в неделю"""
    try:
        is_valid, days = validate_training_days(text)

        if not is_valid:
            await message.answer(
                "❌ Количество дней должно быть числом от 1 до 7.\n"
                "Пожалуйста, введите корректное значение:"
            )
            return

        dialog_manager.dialog_data["training_days_per_week"] = days
        await dialog_manager.next()

    except (ValueError, TypeError) as e:
        logger.error(f"Error validating training days: {e}")
        await message.answer(
            "❌ Неверный формат.\n" "Пожалуйста, введите число от 1 до 7 дней:"
        )


async def on_training_type_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора типа тренировок"""
    try:
        dialog_manager.dialog_data["preferred_training_type"] = item_id
        await callback.answer("✅ Тип тренировок сохранен!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in training type selection: {e}")
        await callback.answer("❌ Ошибка при выборе типа")


async def on_training_difficulty_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора сложности тренировок"""
    try:
        dialog_manager.dialog_data["preferred_difficulty"] = item_id
        await callback.answer("✅ Сложность тренировок сохранена!")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in training difficulty selection: {e}")
        await callback.answer("❌ Ошибка при выборе сложности")


# Обработчики для группы 4: Здоровье


async def on_injuries_input(
    message: Message, widget: MessageInput, dialog_manager: DialogManager, text: str
):
    """Обработка ввода информации о травмах"""
    try:
        description = text.strip()
        dialog_manager.dialog_data["injuries_description"] = (
            description if description else None
        )
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in injuries input: {e}")
        await message.answer("❌ Ошибка при сохранении информации о травмах")


async def on_flexibility_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора уровня гибкости"""
    try:
        dialog_manager.dialog_data["flexibility_level"] = item_id
        display_name = FLEXIBILITY_DISPLAY_MAP.get(item_id, item_id)
        await callback.answer(f"✅ Гибкость: {display_name}")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in flexibility selection: {e}")
        await callback.answer("❌ Ошибка при выборе уровня гибкости")


async def on_endurance_selected(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    """Обработка выбора уровня выносливости"""
    try:
        dialog_manager.dialog_data["endurance_level"] = item_id
        display_name = FLEXIBILITY_DISPLAY_MAP.get(
            item_id, item_id
        )  # Используем ту же карту
        await callback.answer(f"✅ Выносливость: {display_name}")
        await dialog_manager.next()

    except Exception as e:
        logger.error(f"Error in endurance selection: {e}")
        await callback.answer("❌ Ошибка при выборе уровня выносливости")


# Обработчики для окна подтверждения


async def get_summary_data(dialog_manager: DialogManager, **kwargs):
    """Подготовка данных для отображения в окне подтверждения"""
    data = dialog_manager.dialog_data
    summary = []

    # Функция для добавления элемента в сводку
    def add_item(label, value, condition=True):
        if condition and value is not None:
            summary.append({"label": label, "value": str(value)})

    # Группа 1: Основные данные
    add_item("📅 Возраст", f"{data.get('age')} лет", "age" in data)

    if "gender" in data:
        gender_display = {
            "male": "👨 Мужской",
            "female": "👩 Женский",
            "other": "🏳️‍🌈 Другой",
        }.get(data["gender"], data["gender"])
        add_item("🧑‍🤝‍🧑 Пол", gender_display)

    add_item("📏 Рост", f"{data.get('height_cm')} см", "height_cm" in data)
    add_item("⚖️ Вес", f"{data.get('weight_kg')} кг", "weight_kg" in data)
    add_item(
        "🎯 Целевой вес",
        f"{data.get('target_weight_kg')} кг",
        "target_weight_kg" in data,
    )

    if "body_type" in data:
        body_type_display = {
            "ectomorph": "📐 Эктоморф (худощавый)",
            "mesomorph": "📦 Мезоморф (мускулистый)",
            "endomorph": "📦 Эндоморф (склонный к полноте)",
            "unknown": "❓ Не знаю",
        }.get(data["body_type"], data["body_type"])
        add_item("🧬 Тип телосложения", body_type_display)

    # Группа 2: Цели и образ жизни
    if "goal" in data:
        goal_display = GOAL_DISPLAY_MAP.get(data["goal"], data["goal"])
        add_item("🎯 Цель", goal_display)

    if "lifestyle" in data:
        lifestyle_display = LIFESTYLE_DISPLAY_MAP.get(
            data["lifestyle"], data["lifestyle"]
        )
        add_item("🏃 Образ жизни", lifestyle_display)

    add_item("😴 Часы сна", f"{data.get('sleep_hours')} ч", "sleep_hours" in data)

    if data.get("genetics_description"):
        genetics_text = data["genetics_description"]
        if len(genetics_text) > 50:
            genetics_text = genetics_text[:47] + "..."
        add_item("🧬 Генетика", genetics_text)

    if "is_experienced_training" in data:
        exp_display = (
            "✅ Есть опыт" if data["is_experienced_training"] else "❌ Нет опыта"
        )
        add_item("💪 Опыт тренировок", exp_display)

    if "last_ideal_form_date" in data:
        date_value = data["last_ideal_form_date"]
        if date_value:
            date_str = date_value.strftime("%d.%m.%Y")
            add_item("📅 Последняя идеальная форма", date_str)
        else:
            add_item("📅 Последняя идеальная форма", "Никогда")

    # Добавьте остальные группы аналогичным образом...

    return {"summary_items": summary, "items_count": len(summary)}


async def on_confirmation_save(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
):
    """Сохранение анкеты в БД"""
    user_id = callback.from_user.id
    data = dialog_manager.dialog_data

    logger.info(f"Saving profile for user {user_id}")

    # Значения по умолчанию для обязательных полей
    defaults = {
        "goal": "unknown",
        "lifestyle": "sedentary",
        "sleep_hours": 7.0,
        "is_experienced_training": False,
        "training_days_per_week": 3,
        "profile_completed": True,
        "completed_at": datetime.utcnow(),
    }

    # Объединяем данные с дефолтами
    data_to_save = {**defaults, **data}

    try:
        async with async_session_maker() as session:
            # Находим пользователя
            stmt_user = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt_user)
            user = result.scalar_one_or_none()

            if not user:
                logger.error(f"User {user_id} not found in database")
                await callback.answer("❌ Пользователь не найден!")
                return

            # Проверяем существующий профиль
            stmt_profile = select(UserProfile).where(UserProfile.user_id == user.id)
            result = await session.execute(stmt_profile)
            profile = result.scalar_one_or_none()

            # Обновляем или создаем профиль
            if profile:
                # Обновляем существующий профиль
                for key, value in data_to_save.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                profile.updated_at = datetime.utcnow()
                logger.info(f"Updated existing profile for user {user_id}")
            else:
                # Создаем новый профиль
                profile_data = {
                    k: v for k, v in data_to_save.items() if hasattr(UserProfile, k)
                }
                profile = UserProfile(user_id=user.id, **profile_data)
                session.add(profile)
                logger.info(f"Created new profile for user {user_id}")

            await session.commit()
            logger.info(f"Profile successfully saved for user {user_id}")

            await callback.answer("✅ Анкета успешно сохранена!")
            await dialog_manager.done()

            # Отправляем финальное сообщение
            await callback.message.answer(
                "🎉 <b>Анкета успешно сохранена!</b>\n\n"
                "Теперь вы можете получить персонализированный план тренировок и питания.\n\n"
                "Нажмите <b>🏋️ Мой план</b> для получения тренировочного плана.",
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error saving profile for user {user_id}: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при сохранении анкеты!")


async def on_confirmation_edit(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
):
    """Возврат к редактированию анкеты"""
    try:
        from .states import QuestionnaireStates

        await dialog_manager.switch_to(QuestionnaireStates.age)
        await callback.answer("✏️ Редактируйте анкету с начала")
    except Exception as e:
        logger.error(f"Error switching to edit mode: {e}")
        await callback.answer("❌ Ошибка при переходе к редактированию")


# Алиас для совместимости
getter_summary = get_summary_data

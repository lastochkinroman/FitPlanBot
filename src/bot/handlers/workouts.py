"""Хэндлеры для планов тренировок и питания"""

from aiogram import F, Router, types
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.bot.keyboards.main_menu import get_main_menu_kb
from src.database.models import User, UserProfile
from src.database.session import async_session_maker
from src.services.file_service import file_service
from src.services.matching import MatchingService

router = Router()


# Вспомогательные функции
def format_workout_schedule(schedule: dict) -> str:
    """Форматирует расписание тренировок"""
    if not schedule:
        return "Расписание не указано"

    days_map = {
        "day1": "🏋️ Понедельник",
        "day2": "💪 Вторник",
        "day3": "🦵 Среда",
        "day4": "🏃 Четверг",
        "day5": "🤸 Пятница",
        "day6": "🏊 Суббота",
        "day7": "🚶 Воскресенье",
    }

    formatted = []
    for day_key, day_data in schedule.items():
        day_name = days_map.get(day_key, day_key)

        if isinstance(day_data, dict) and "exercises" in day_data:
            exercises = day_data["exercises"][:5]
            ex_list = "\n".join(f"• {ex}" for ex in exercises)
            if len(day_data["exercises"]) > 5:
                ex_list += f"\n• ... и ещё {len(day_data['exercises']) - 5}"
            formatted.append(f"{day_name}:\n{ex_list}")
        else:
            formatted.append(
                f"{day_name}: Отдых" if not day_data else f"{day_name}: {day_data}"
            )

    return "\n\n".join(formatted)


def format_video_links(links: dict) -> str:
    """Форматирует видео-ссылки"""
    if not links:
        return ""

    video_links = [
        f"• {key}: {url}"
        for key, url in links.items()
        if isinstance(url, str) and url.startswith("http")
    ]

    return "\n\n🎥 Видео-уроки:\n" + "\n".join(video_links) if video_links else ""


# Основные хэндлеры
@router.message(F.text == "🏋️ Мой план")
async def show_workout_plan(message: types.Message):
    """Показывает персональный план тренировок"""
    async with async_session_maker() as session:
        # Получаем пользователя с профилем
        stmt = (
            select(User)
            .where(User.telegram_id == message.from_user.id)
            .options(selectinload(User.profile))
        )
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            return await message.answer("❌ Пользователь не найден. Используйте /start")

        if not user.profile:
            return await message.answer(
                "📝 Для получения плана заполните анкету",
                reply_markup=get_main_menu_kb(),
            )

        if not user.profile.profile_completed:
            return await message.answer(
                "⏳ Завершите заполнение анкеты", reply_markup=get_main_menu_kb()
            )

        # Ищем подходящий план
        matching = MatchingService(session)
        workout_plan = await matching.get_workout_plan_for_user(user.profile)

        if not workout_plan:
            return await message.answer(
                "🔍 Подбираем план... Попробуйте позже", reply_markup=get_main_menu_kb()
            )

        # Формируем ответ
        response = [
            f"🏋️ <b>{workout_plan.name}</b>",
            f"{workout_plan.description or ''}",
            "📅 <b>Расписание:</b>",
            format_workout_schedule(workout_plan.schedule or {}),
            format_video_links(workout_plan.video_links or {}),
        ]

        if workout_plan.target_goal:
            goals = (
                workout_plan.target_goal
                if isinstance(workout_plan.target_goal, list)
                else []
            )
            if goals:
                response.append(f"🎯 <b>Цели:</b> {', '.join(goals)}")

        response.append("\n💪 Удачи в тренировках!")

        await message.answer(
            "\n\n".join(filter(None, response)),
            parse_mode="HTML",
            reply_markup=get_main_menu_kb(),
        )


@router.message(F.text == "🍎 Питание")
async def show_meal_plan(message: types.Message):
    """Показывает персональный план питания"""
    async with async_session_maker() as session:
        # Получаем пользователя
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            return await message.answer("❌ Пользователь не найден. Используйте /start")

        # Получаем профиль отдельно
        stmt_profile = select(UserProfile).where(UserProfile.user_id == user.id)
        profile = (await session.execute(stmt_profile)).scalar_one_or_none()

        if not profile:
            return await message.answer(
                "📝 Для получения плана заполните анкету",
                reply_markup=get_main_menu_kb(),
            )

        if not profile.profile_completed:
            return await message.answer(
                "⏳ Завершите заполнение анкеты", reply_markup=get_main_menu_kb()
            )

        # Ищем план питания
        matching = MatchingService(session)
        meal_plan = await matching.get_meal_plan_for_user(profile)

        if not meal_plan:
            return await message.answer(
                "🔍 Подбираем план... Попробуйте позже", reply_markup=get_main_menu_kb()
            )

        # Формируем ответ
        response = [
            f"🍎 <b>{meal_plan.name}</b>",
            f"{meal_plan.description or ''}",
        ]

        if (
            meal_plan.calories_range
            and isinstance(meal_plan.calories_range, list)
            and len(meal_plan.calories_range) >= 2
        ):
            response.append(
                f"🔥 <b>Калории:</b> {meal_plan.calories_range[0]}-{meal_plan.calories_range[1]} ккал/день"
            )

        if meal_plan.target_goal:
            goals = (
                meal_plan.target_goal if isinstance(meal_plan.target_goal, list) else []
            )
            if goals:
                response.append(f"🎯 <b>Цели:</b> {', '.join(goals)}")

        response.append("\n🥗 <b>Советы:</b>")
        response.append("• Пейте достаточно воды")
        response.append("• Регулярное питание")
        response.append("• Сбалансированный рацион")

        await message.answer(
            "\n\n".join(response), parse_mode="HTML", reply_markup=get_main_menu_kb()
        )

        # Отправляем PDF если есть
        if meal_plan.pdf_file_path:
            pdf_path = file_service.get_pdf_path(meal_plan.pdf_file_path)
            if pdf_path:
                try:
                    await message.answer_document(
                        types.FSInputFile(pdf_path),
                        caption="📄 Подробный план питания",
                        parse_mode="HTML",
                    )
                except:
                    pass  # Просто пропускаем ошибку отправки файла

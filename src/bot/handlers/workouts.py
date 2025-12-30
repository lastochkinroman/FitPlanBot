import os
from pathlib import Path
from aiogram import Router, types, F
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.session import async_session_maker
from src.database.models import User, UserProfile
from src.services.matching import MatchingService
from src.services.file_service import file_service
from src.bot.keyboards.main_menu import get_main_menu_kb

router = Router()


def format_workout_schedule(schedule: dict) -> str:
    """
    Форматирует расписание тренировок в читаемый вид
    """
    if not schedule:
        return "Расписание не указано"

    formatted_days = []
    for day_key, day_data in schedule.items():
        day_name = {
            "day1": "🏋️ Понедельник",
            "day2": "💪 Вторник",
            "day3": "🦵 Среда",
            "day4": "🏃 Четверг",
            "day5": "🤸 Пятница",
            "day6": "🏊 Суббота",
            "day7": "🚶 Воскресенье"
        }.get(day_key, day_key)

        if isinstance(day_data, dict):
            exercises = day_data.get("exercises", [])
            if exercises:
                exercise_list = "\n".join(f"• {ex}" for ex in exercises[:5])  # Ограничим 5 упражнениями
                if len(exercises) > 5:
                    exercise_list += f"\n• ... и ещё {len(exercises) - 5} упражнений"
                formatted_days.append(f"{day_name}:\n{exercise_list}")
            else:
                formatted_days.append(f"{day_name}: Отдых")
        else:
            formatted_days.append(f"{day_name}: {day_data}")

    return "\n\n".join(formatted_days)


def format_video_links(video_links: dict) -> str:
    """
    Форматирует ссылки на видео
    """
    if not video_links:
        return ""

    links = []
    for key, url in video_links.items():
        if isinstance(url, str) and url.startswith("http"):
            links.append(f"• {key}: {url}")

    if links:
        return "\n\n🎥 Видео-уроки:\n" + "\n".join(links)

    return ""


@router.message(F.text == "🏋️ Мой план")
async def show_workout_plan(message: types.Message):
    """
    Показывает персональный план тренировок
    """
    print(f"WORKOUT HANDLER: Started for user {message.from_user.id}")
    user_id = message.from_user.id

    async with async_session_maker() as session:
        print(f"WORKOUT HANDLER: Session created")
        # Получаем пользователя с профилем
        stmt = select(User).where(User.telegram_id == user_id).options(
            selectinload(User.profile)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ <b>Пользователь не найден</b>\n\n"
                "Попробуйте перезапустить бота командой /start",
                parse_mode="HTML"
            )
            return

        print(f"DEBUG: User found: {user.id}, telegram_id: {user.telegram_id}")
        print(f"DEBUG: User profile exists: {user.profile is not None}")

        if not user.profile:
            print("DEBUG: No profile found, asking to fill questionnaire")
            await message.answer(
                "📝 <b>Анкета не заполнена</b>\n\n"
                "Чтобы получить персональный план тренировок, нужно:\n"
                "1️⃣ Заполнить анкету с вашими данными\n"
                "2️⃣ Активировать подписку\n\n"
                "Нажмите <b>'📝 Заполнить анкету'</b> для начала!",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        print(f"DEBUG: Profile completed: {user.profile.profile_completed}")

        if not user.profile.profile_completed:
            print("DEBUG: Profile not completed, asking to complete questionnaire")
            await message.answer(
                "⏳ <b>Анкета заполняется</b>\n\n"
                "Завершите заполнение анкеты, чтобы получить план тренировок.",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        # Создаем сервис подбора и ищем план
        matching_service = MatchingService(session)
        print(f"DEBUG: Profile completed: {user.profile.profile_completed}")
        print(f"DEBUG: Profile goal: {user.profile.goal}")
        print(f"DEBUG: Profile difficulty: {user.profile.preferred_difficulty}")
        print(f"DEBUG: Profile body_type: {user.profile.body_type}")

        # Проверим, есть ли планы в БД
        all_plans = await matching_service.get_all_active_workout_plans()
        print(f"DEBUG: Total active workout plans: {len(all_plans)}")

        workout_plan = await matching_service.get_workout_plan_for_user(user.profile)

        if not workout_plan:
            await message.answer(
                f"🔍 <b>План тренировок подбирается</b>\n\n"
                f"У вас есть {len(all_plans)} активных планов в системе.\n"
                f"Ваш профиль: цель={user.profile.goal}, уровень={user.profile.preferred_difficulty}\n\n"
                "Мы подбираем оптимальный план тренировок под ваши цели и уровень подготовки.\n"
                "Попробуйте позже или обратитесь в поддержку.\n\n"
                "<i>Возможно, нужно добавить больше планов в систему.</i>",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        # Форматируем ответ
        response = f"🏋️ <b>{workout_plan.name}</b>\n\n"

        if workout_plan.description:
            response += f"{workout_plan.description}\n\n"

        response += "📅 <b>Расписание тренировок:</b>\n\n"

        if workout_plan.schedule:
            schedule_text = format_workout_schedule(workout_plan.schedule)
            response += schedule_text
        else:
            response += "Расписание не указано"

        # Добавляем видео-ссылки
        if workout_plan.video_links:
            video_text = format_video_links(workout_plan.video_links)
            response += video_text

        # Добавляем информацию о цели и уровне
        response += "\n\n🎯 <b>Рекомендации:</b>\n"
        if workout_plan.target_goal:
            goals = workout_plan.target_goal if isinstance(workout_plan.target_goal, list) else []
            if goals:
                response += f"• Подходит для целей: {', '.join(goals)}\n"

        if workout_plan.target_level:
            levels = workout_plan.target_level if isinstance(workout_plan.target_level, list) else []
            if levels:
                response += f"• Уровень сложности: {', '.join(levels)}\n"

        response += "\n💪 <b>Удачи в тренировках!</b>\n"
        response += "<i>Следите за прогрессом и корректируйте нагрузку по самочувствию.</i>"

        await message.answer(
            response,
            parse_mode="HTML",
            reply_markup=get_main_menu_kb()
        )


@router.message(F.text == "🍎 Питание")
async def show_meal_plan(message: types.Message):
    """
    Показывает персональный план питания
    """
    print(f"WORKOUT HANDLER: Meal plan started for user {message.from_user.id}")
    user_id = message.from_user.id

    async with async_session_maker() as session:
        # Получаем пользователя с профилем
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ <b>Пользователь не найден</b>\n\n"
                "Попробуйте перезапустить бота командой /start",
                parse_mode="HTML"
            )
            return

        # Загружаем профиль отдельно
        stmt_profile = select(UserProfile).where(UserProfile.user_id == user.id)
        result_profile = await session.execute(stmt_profile)
        user.profile = result_profile.scalar_one_or_none()

        if not user.profile:
            await message.answer(
                "📝 <b>Анкета не заполнена</b>\n\n"
                "Чтобы получить персональный план питания, нужно:\n"
                "1️⃣ Заполнить анкету с вашими данными\n"
                "2️⃣ Активировать подписку\n\n"
                "Нажмите <b>'📝 Заполнить анкету'</b> для начала!",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        if not user.profile.profile_completed:
            await message.answer(
                "⏳ <b>Анкета заполняется</b>\n\n"
                "Завершите заполнение анкеты, чтобы получить план питания.",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        # Создаем сервис подбора и ищем план
        matching_service = MatchingService(session)
        meal_plan = await matching_service.get_meal_plan_for_user(user.profile)

        if not meal_plan:
            await message.answer(
                f"🔍 <b>План питания подбирается</b>\n\n"
                f"Ваш профиль: цель={user.profile.goal}\n\n"
                "Мы подбираем оптимальный план питания под ваши цели.\n"
                "Попробуйте позже или обратитесь в поддержку.\n\n"
                "<i>Возможно, нужно добавить больше планов в систему.</i>",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )
            return

        # Форматируем ответ
        response = f"🍎 <b>{meal_plan.name}</b>\n\n"

        if meal_plan.description:
            response += f"{meal_plan.description}\n\n"

        if meal_plan.calories_range:
            calories = meal_plan.calories_range
            if isinstance(calories, list) and len(calories) >= 2:
                response += f"🔥 <b>Калории:</b> {calories[0]}-{calories[1]} ккал/день\n\n"

        response += "🍽️ <b>Рекомендации по питанию:</b>\n"
        if meal_plan.target_goal:
            goals = meal_plan.target_goal if isinstance(meal_plan.target_goal, list) else []
            if goals:
                response += f"• Подходит для целей: {', '.join(goals)}\n"

        response += "\n🥗 <b>Советы:</b>\n"
        response += "• Пейте достаточное количество воды\n"
        response += "• Ешьте регулярно, не пропускайте приемы пищи\n"
        response += "• Следите за балансом белков, жиров и углеводов\n"
        response += "• Включайте овощи и фрукты в каждый прием пищи\n\n"

        response += "<i>План питания адаптирован под ваши индивидуальные параметры.</i>"

        await message.answer(
            response,
            parse_mode="HTML",
            reply_markup=get_main_menu_kb()
        )

        # Отправляем PDF файл если есть
        if meal_plan.pdf_file_path:
            pdf_path = file_service.get_pdf_path(meal_plan.pdf_file_path)
            if pdf_path:
                try:
                    await message.answer_document(
                        document=types.FSInputFile(pdf_path),
                        caption="📄 <b>Подробный план питания (PDF)</b>",
                        parse_mode="HTML"
                    )
                    print(f"Sent PDF file: {meal_plan.pdf_file_path}")
                except Exception as e:
                    print(f"Error sending PDF: {e}")
                    await message.answer(
                        "⚠️ Не удалось отправить PDF файл плана питания",
                        reply_markup=get_main_menu_kb()
                    )

        # Отправляем изображения если есть (закомментировано для тестирования)
        # if meal_plan.image_file_paths:
        #     image_paths = file_service.get_image_paths(meal_plan.image_file_paths)
        #     for i, image_path in enumerate(image_paths[:3]):  # Максимум 3 изображения
        #         try:
        #             await message.answer_photo(
        #                 photo=types.FSInputFile(image_path),
        #                 caption=f"🖼️ <b>Пример рациона {i+1}</b>",
        #                 parse_mode="HTML"
        #             )
        #             print(f"Sent image file: {image_path}")
        #         except Exception as e:
        #             print(f"Error sending image {i+1}: {e}")

        # Если есть файлы, отправляем финальное сообщение
        if meal_plan.pdf_file_path or (meal_plan.image_file_paths and file_service.get_image_paths(meal_plan.image_file_paths)):
            await message.answer(
                "📋 <b>Файлы плана питания отправлены!</b>\n\n"
                "Изучите материалы и следуйте рекомендациям.\n"
                "При необходимости скорректируйте рацион под свои предпочтения.",
                parse_mode="HTML",
                reply_markup=get_main_menu_kb()
            )

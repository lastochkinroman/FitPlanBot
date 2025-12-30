#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в базу данных
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.database.session import async_session_maker
from src.database.models import WorkoutPlan


async def add_test_workout_plans():
    """Добавляет тестовые планы тренировок"""
    async with async_session_maker() as session:
        # Проверяем, есть ли уже планы
        from sqlalchemy import select
        result = await session.execute(select(WorkoutPlan))
        existing_plans = result.scalars().all()

        if existing_plans:
            print(f"Уже есть {len(existing_plans)} планов тренировок")
            return

        # Создаем тестовые планы
        plans_data = [
            {
                "name": "Программа для похудения - Новички",
                "description": "Комплексная программа для начинающих, направленная на снижение веса через кардио и силовые тренировки",
                "target_goal": ["lose_weight"],
                "target_level": ["beginner"],
                "target_body_type": ["ectomorph", "mesomorph", "endomorph"],
                "schedule": {
                    "day1": {"exercises": ["Приседания 3x15", "Отжимания от колен 3x10", "Планка 3x30сек", "Бег на месте 5 мин"]},
                    "day2": {"exercises": ["Выпады 3x12", "Подтягивания в гравитроне 3x8", "Скручивания 3x20", "Прыжки на скакалке 5 мин"]},
                    "day3": "Отдых",
                    "day4": {"exercises": ["Приседания с прыжком 3x10", "Отжимания 3x8", "Берпи 3x8", "Кардио 10 мин"]},
                    "day5": {"exercises": ["Ягодичный мостик 3x15", "Планка с подъемом ног 3x10", "Велосипед 3x20", "Бег трусцой 15 мин"]},
                    "day6": {"exercises": ["Приседания сумо 3x12", "Разведение рук с гантелями 3x15", "Русские скручивания 3x20", "Интервальный бег 10 мин"]},
                    "day7": "Отдых"
                },
                "video_links": {
                    "Кардио тренировка": "https://example.com/cardio",
                    "Силовая тренировка": "https://example.com/strength",
                    "Техника выполнения": "https://example.com/technique"
                },
                "is_active": True
            },
            {
                "name": "Программа набора массы - Продвинутые",
                "description": "Интенсивная программа для опытных атлетов, направленная на набор мышечной массы",
                "target_goal": ["gain_muscle"],
                "target_level": ["intermediate", "advanced"],
                "target_body_type": ["mesomorph"],
                "schedule": {
                    "day1": {"exercises": ["Приседания со штангой 4x8-10", "Жим ногами 4x10", "Румынская тяга 4x8", "Икры 3x15"]},
                    "day2": {"exercises": ["Жим штанги лежа 4x8-10", "Жим гантелей на наклонной 4x10", "Армейский жим 4x8", "Разведение рук 3x12"]},
                    "day3": {"exercises": ["Тяга штанги в наклоне 4x8", "Подтягивания 4x8-10", "Тяга гантели одной рукой 4x10", "Шраги 3x12"]},
                    "day4": {"exercises": ["Приседания фронтальные 4x8", "Жим ногами узко 4x10", "Сгибания ног лежа 4x10", "Икры на икры 3x15"]},
                    "day5": {"exercises": ["Жим штанги лежа узко 4x8", "Разведение гантелей лежа 4x10", "Французский жим 4x8", "Бицепс с EZ-грифом 3x10"]},
                    "day6": {"exercises": ["Становая тяга 4x6-8", "Тяга верхнего блока 4x10", "Лицевая тяга 3x12", "Упражнение на дельты 3x12"]},
                    "day7": "Отдых"
                },
                "video_links": {
                    "Техника жима лежа": "https://example.com/bench-press",
                    "Становая тяга": "https://example.com/deadlift",
                    "Программа тренировок": "https://example.com/full-program"
                },
                "is_active": True
            }
        ]

        for plan_data in plans_data:
            plan = WorkoutPlan(**plan_data)
            session.add(plan)

        await session.commit()
        print(f"Добавлено {len(plans_data)} тестовых планов тренировок")


if __name__ == "__main__":
    asyncio.run(add_test_workout_plans())

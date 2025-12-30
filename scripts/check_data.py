#!/usr/bin/env python3
"""
Скрипт для проверки данных в базе данных
"""
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.database.session import async_session_maker
from src.database.models import MealPlan, WorkoutPlan


async def check_meal_plans():
    """Проверяет планы питания"""
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(MealPlan))
        plans = result.scalars().all()

        print(f"Найдено планов питания: {len(plans)}")
        for plan in plans:
            print(f"- {plan.name}")
            print(f"  PDF: {plan.pdf_file_path}")
            print(f"  Images: {plan.image_file_paths}")
            print(f"  Calories: {plan.calories_range}")
            print()


async def check_workout_plans():
    """Проверяет планы тренировок"""
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(WorkoutPlan))
        plans = result.scalars().all()

        print(f"Найдено планов тренировок: {len(plans)}")
        for plan in plans:
            print(f"- {plan.name}")
            print(f"  Target goal: {plan.target_goal}")
            print(f"  Target level: {plan.target_level}")
            print()


async def main():
    print("=== ПРОВЕРКА ДАННЫХ В БАЗЕ ===\n")
    await check_workout_plans()
    await check_meal_plans()


if __name__ == "__main__":
    asyncio.run(main())

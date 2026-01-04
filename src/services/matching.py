"""Сервис для подбора планов тренировок и питания"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import MealPlan, UserProfile, WorkoutPlan


class MatchingService:
    """Простой подбор планов по целям пользователя"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workout_plan_for_user(
        self, profile: UserProfile
    ) -> Optional[WorkoutPlan]:
        """
        Подбирает план тренировок по цели пользователя
        """
        if not profile or not profile.goal:
            return None

        # Простой запрос - ищем план с подходящей целью
        stmt = select(WorkoutPlan).where(WorkoutPlan.is_active == True)
        result = await self.session.execute(stmt)
        plans = result.scalars().all()

        # Сначала ищем точное совпадение по цели
        for plan in plans:
            if plan.target_goal and profile.goal in plan.target_goal:
                return plan

        # Если не нашли - возвращаем любой активный план
        return plans[0] if plans else None

    async def get_meal_plan_for_user(self, profile: UserProfile) -> Optional[MealPlan]:
        """
        Подбирает план питания по цели пользователя
        """
        if not profile or not profile.goal:
            return None

        stmt = select(MealPlan).where(MealPlan.is_active == True)
        result = await self.session.execute(stmt)
        plans = result.scalars().all()

        # Ищем план с подходящей целью
        for plan in plans:
            if plan.target_goal and profile.goal in plan.target_goal:
                return plan

        return plans[0] if plans else None

    async def get_all_active_workout_plans(self) -> List[WorkoutPlan]:
        """Все активные планы тренировок"""
        stmt = select(WorkoutPlan).where(WorkoutPlan.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

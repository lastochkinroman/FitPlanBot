from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from src.database.models import WorkoutPlan, MealPlan, UserProfile
import logging

logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_workout_plan_for_user(self, profile: UserProfile) -> Optional[WorkoutPlan]:
        """
        Подбирает план тренировок для пользователя на основе его профиля
        """
        if not profile or not profile.profile_completed:
            logger.info("Profile not completed, cannot match workout plan")
            return None

        # Основные критерии подбора
        goal = profile.goal
        difficulty = profile.preferred_difficulty
        body_type = profile.body_type
        experience = profile.is_experienced_training

        logger.info(f"Matching workout plan for user with goal={goal}, difficulty={difficulty}, body_type={body_type}, experience={experience}")

        # Запрос планов с учетом критериев
        stmt = select(WorkoutPlan).where(
            WorkoutPlan.is_active == True
        ).order_by(WorkoutPlan.created_at.desc())

        result = await self.session.execute(stmt)
        plans = result.scalars().all()

        # Фильтрация и ранжирование планов
        scored_plans = []
        for plan in plans:
            score = self._calculate_workout_plan_score(plan, profile)
            if score > 0:  # Только планы с положительным совпадением
                scored_plans.append((plan, score))

        # Сортировка по убыванию совпадения
        scored_plans.sort(key=lambda x: x[1], reverse=True)

        if scored_plans:
            best_plan = scored_plans[0][0]
            logger.info(f"Selected workout plan: {best_plan.name} (score: {scored_plans[0][1]})")
            return best_plan

        logger.info("No suitable workout plan found")
        return None

    def _calculate_workout_plan_score(self, plan: WorkoutPlan, profile: UserProfile) -> float:
        """
        Рассчитывает степень совпадения плана с профилем пользователя
        Возвращает score от 0 до 1
        """
        score = 0.0
        total_weight = 0.0

        # 1. Совпадение по цели (вес 0.4)
        if plan.target_goal and profile.goal:
            plan_goals = plan.target_goal if isinstance(plan.target_goal, list) else []
            if profile.goal in plan_goals:
                score += 0.4
            total_weight += 0.4

        # 2. Совпадение по уровню сложности (вес 0.3)
        if plan.target_level and profile.preferred_difficulty:
            plan_levels = plan.target_level if isinstance(plan.target_level, list) else []
            if profile.preferred_difficulty in plan_levels:
                score += 0.3
            total_weight += 0.3

        # 3. Совпадение по типу телосложения (вес 0.2)
        if plan.target_body_type and profile.body_type:
            plan_body_types = plan.target_body_type if isinstance(plan.target_body_type, list) else []
            if profile.body_type in plan_body_types:
                score += 0.2
            total_weight += 0.2

        # 4. Учет опыта тренировок (вес 0.1)
        # Для новичков предпочтительнее простые планы, для опытных - сложные
        if profile.preferred_difficulty and profile.is_experienced_training is not None:
            expected_level = "intermediate" if profile.is_experienced_training else "beginner"
            if profile.preferred_difficulty == expected_level:
                score += 0.1
            total_weight += 0.1

        # Нормализация по общему весу
        if total_weight > 0:
            score = score / total_weight

        return score

    async def get_meal_plan_for_user(self, profile: UserProfile) -> Optional[MealPlan]:
        """
        Подбирает план питания для пользователя на основе его профиля
        """
        if not profile or not profile.profile_completed:
            logger.info("Profile not completed, cannot match meal plan")
            return None

        # Основные критерии подбора
        goal = profile.goal
        calories_preference = self._estimate_calories_range(profile)

        logger.info(f"Matching meal plan for user with goal={goal}, estimated calories={calories_preference}")

        # Запрос планов с учетом критериев
        stmt = select(MealPlan).where(
            MealPlan.is_active == True
        ).order_by(MealPlan.created_at.desc())

        result = await self.session.execute(stmt)
        plans = result.scalars().all()

        # Фильтрация и ранжирование планов
        scored_plans = []
        for plan in plans:
            score = self._calculate_meal_plan_score(plan, profile, calories_preference)
            if score > 0:
                scored_plans.append((plan, score))

        # Сортировка по убыванию совпадения
        scored_plans.sort(key=lambda x: x[1], reverse=True)

        if scored_plans:
            best_plan = scored_plans[0][0]
            logger.info(f"Selected meal plan: {best_plan.name} (score: {scored_plans[0][1]})")
            return best_plan

        logger.info("No suitable meal plan found")
        return None

    def _estimate_calories_range(self, profile: UserProfile) -> tuple[int, int]:
        """
        Оценивает диапазон калорий на основе профиля
        """
        if not profile.weight_kg or not profile.height_cm or not profile.age or not profile.gender:
            return (1800, 2500)  # Значения по умолчанию

        # Простая формула расчета базового метаболизма (BMR)
        if profile.gender == 'male':
            bmr = 88.362 + (13.397 * profile.weight_kg) + (4.799 * profile.height_cm) - (5.677 * profile.age)
        else:
            bmr = 447.593 + (9.247 * profile.weight_kg) + (3.098 * profile.height_cm) - (4.330 * profile.age)

        # Учет активности
        activity_multiplier = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }.get(profile.lifestyle or 'sedentary', 1.2)

        tdee = bmr * activity_multiplier

        # Корректировка по цели
        if profile.goal == 'lose_weight':
            calories = tdee - 500  # Дефицит для похудения
        elif profile.goal == 'gain_muscle':
            calories = tdee + 300  # Профицит для набора массы
        else:
            calories = tdee  # Поддержание

        # Диапазон ±10%
        min_calories = int(calories * 0.9)
        max_calories = int(calories * 1.1)

        return (min_calories, max_calories)

    def _calculate_meal_plan_score(self, plan: MealPlan, profile: UserProfile, calories_range: tuple[int, int]) -> float:
        """
        Рассчитывает степень совпадения плана питания с профилем
        """
        score = 0.0
        total_weight = 0.0

        # 1. Совпадение по цели (вес 0.5)
        if plan.target_goal and profile.goal:
            plan_goals = plan.target_goal if isinstance(plan.target_goal, list) else []
            if profile.goal in plan_goals:
                score += 0.5
            total_weight += 0.5

        # 2. Совпадение по калориям (вес 0.4)
        if plan.calories_range:
            plan_calories = plan.calories_range if isinstance(plan.calories_range, list) else []
            if len(plan_calories) >= 2:
                plan_min, plan_max = plan_calories[0], plan_calories[1]
                user_min, user_max = calories_range

                # Проверка пересечения диапазонов
                if max(plan_min, user_min) <= min(plan_max, user_max):
                    overlap = min(plan_max, user_max) - max(plan_min, user_min)
                    total_range = user_max - user_min
                    if total_range > 0:
                        overlap_score = overlap / total_range
                        score += 0.4 * overlap_score
                total_weight += 0.4

        # 3. Совпадение по типу телосложения (вес 0.1)
        # Планы питания могут быть общими, поэтому небольшой вес
        if profile.body_type and profile.body_type != 'unknown':
            score += 0.1 * 0.5  # Частичное совпадение для любого плана
            total_weight += 0.1

        # Нормализация
        if total_weight > 0:
            score = score / total_weight

        return score

    async def get_all_active_workout_plans(self) -> List[WorkoutPlan]:
        """
        Получает все активные планы тренировок
        """
        stmt = select(WorkoutPlan).where(WorkoutPlan.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_active_meal_plans(self) -> List[MealPlan]:
        """
        Получает все активные планы питания
        """
        stmt = select(MealPlan).where(MealPlan.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

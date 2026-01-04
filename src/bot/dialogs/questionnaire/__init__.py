"""Диалог анкеты пользователя (24 вопроса, разбитые на 4 группы)"""

from aiogram_dialog import Dialog

from .states import QuestionnaireStates
from .windows import (  # Группа 1: Основные данные; Группа 2: Цели и образ жизни; Группа 3: Тренировки; Группа 4: Здоровье; Подтверждение
    age_window,
    body_type_window,
    confirmation_window,
    endurance_window,
    experience_window,
    flexibility_window,
    gender_window,
    genetics_window,
    goal_window,
    height_window,
    injuries_window,
    last_form_date_window,
    lifestyle_window,
    sleep_hours_window,
    target_weight_window,
    training_days_window,
    training_difficulty_window,
    training_focus_window,
    training_location_window,
    training_time_window,
    training_type_window,
    weight_window,
)

# Порядок окон соответствует последовательности вопросов в анкете
questionnaire_dialog = Dialog(
    # Группа 1: Основные данные (6 вопросов)
    age_window,
    gender_window,
    height_window,
    weight_window,
    target_weight_window,
    body_type_window,
    # Группа 2: Цели и образ жизни (6 вопросов)
    goal_window,
    lifestyle_window,
    sleep_hours_window,
    genetics_window,
    experience_window,
    last_form_date_window,
    # Группа 3: Тренировки (6 вопросов)
    training_focus_window,
    training_location_window,
    training_time_window,
    training_days_window,
    training_type_window,
    training_difficulty_window,
    # Группа 4: Здоровье (3 вопроса)
    injuries_window,
    flexibility_window,
    endurance_window,
    # Подтверждение (1 окно) - всего 22 окна, но некоторые вопросы могут быть объединены
    confirmation_window,
)

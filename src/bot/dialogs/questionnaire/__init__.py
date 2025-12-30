from aiogram_dialog import Dialog  # Добавьте этот импорт!

from .states import QuestionnaireStates
from .windows import (
    age_window, gender_window, height_window,
    weight_window, target_weight_window, body_type_window,
    goal_window, lifestyle_window, sleep_hours_window,
    genetics_window, experience_window, last_form_date_window,
    training_focus_window, training_location_window, training_time_window,
    training_days_window, training_type_window, training_difficulty_window,
    injuries_window, flexibility_window, endurance_window,
    confirmation_window
)

questionnaire_dialog = Dialog(
    # Группа 1: Основные данные
    age_window,
    gender_window,
    height_window,
    weight_window,
    target_weight_window,
    body_type_window,
    # Группа 2: Цели и образ жизни
    goal_window,
    lifestyle_window,
    sleep_hours_window,
    genetics_window,
    experience_window,
    last_form_date_window,
    # Группа 3: Тренировки
    training_focus_window,
    training_location_window,
    training_time_window,
    training_days_window,
    training_type_window,
    training_difficulty_window,
    # Группа 4: Здоровье
    injuries_window,
    flexibility_window,
    endurance_window,
    # Подтверждение
    confirmation_window,
)

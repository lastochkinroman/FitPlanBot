from aiogram_dialog import Dialog  # Добавьте этот импорт!

from .states import QuestionnaireStates
from .windows import (
    age_window, gender_window, height_window,
    weight_window, target_weight_window, body_type_window,
    confirmation_window
)

questionnaire_dialog = Dialog(
    age_window,
    gender_window,
    height_window,
    weight_window,
    target_weight_window,
    body_type_window,
    confirmation_window,  # Добавляем в конец
)
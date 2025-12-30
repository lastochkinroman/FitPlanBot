from aiogram.fsm.state import StatesGroup, State


class QuestionnaireStates(StatesGroup):
    # Группа 1: Основные данные
    age = State()
    gender = State()
    height = State()
    weight = State()
    target_weight = State()
    body_type = State()
    
    # Группа 2: Цели и образ жизни
    goal = State()
    lifestyle = State()
    sleep_hours = State()
    genetics = State()
    training_experience = State()
    last_ideal_form = State()
    
    # Группа 3: Тренировки
    training_focus = State()
    training_location = State()
    training_time = State()
    training_days = State()
    training_type = State()
    training_difficulty = State()
    
    # Группа 4: Здоровье
    injuries = State()
    flexibility = State()
    endurance = State()
    
    # Группа 5: Подтверждение
    confirmation = State()
    
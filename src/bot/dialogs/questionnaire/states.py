from aiogram.fsm.state import State, StatesGroup


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
    experience = State()  # было training_experience
    last_form_date = State()  # было last_ideal_form

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

    # Методы для удобного доступа к группам состояний
    @classmethod
    def get_group_1_states(cls):
        """Возвращает состояния первой группы (Основные данные)"""
        return [
            cls.age,
            cls.gender,
            cls.height,
            cls.weight,
            cls.target_weight,
            cls.body_type,
        ]

    @classmethod
    def get_group_2_states(cls):
        """Возвращает состояния второй группы (Цели и образ жизни)"""
        return [
            cls.goal,
            cls.lifestyle,
            cls.sleep_hours,
            cls.genetics,
            cls.experience,
            cls.last_form_date,
        ]

    @classmethod
    def get_group_3_states(cls):
        """Возвращает состояния третьей группы (Тренировки)"""
        return [
            cls.training_focus,
            cls.training_location,
            cls.training_time,
            cls.training_days,
            cls.training_type,
            cls.training_difficulty,
        ]

    @classmethod
    def get_group_4_states(cls):
        """Возвращает состояния четвертой группы (Здоровье)"""
        return [
            cls.injuries,
            cls.flexibility,
            cls.endurance,
        ]

    @classmethod
    def get_all_states(cls):
        """Возвращает все состояния анкеты в правильном порядке"""
        return (
            cls.get_group_1_states()
            + cls.get_group_2_states()
            + cls.get_group_3_states()
            + cls.get_group_4_states()
            + [cls.confirmation]
        )

    @classmethod
    def get_state_by_index(cls, index: int) -> State:
        """Получает состояние по индексу (от 0 до 23)"""
        all_states = cls.get_all_states()
        if 0 <= index < len(all_states):
            return all_states[index]
        raise IndexError(f"Index {index} out of range for {len(all_states)} states")

    @classmethod
    def get_next_state(cls, current_state: State) -> State:
        """Получает следующее состояние после текущего"""
        all_states = cls.get_all_states()
        try:
            current_index = all_states.index(current_state)
            if current_index < len(all_states) - 1:
                return all_states[current_index + 1]
        except ValueError:
            pass
        return cls.confirmation  # Если не нашли или это последнее состояние

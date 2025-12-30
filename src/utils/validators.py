from typing import Tuple


def validate_age(text: str) -> Tuple[bool, int]:
    """
    Валидация возраста (14-100 лет)
    Возвращает (is_valid, age)
    """
    try:
        age = int(text.strip())
        if 14 <= age <= 100:
            return True, age
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_height(text: str) -> Tuple[bool, int]:
    """
    Валидация роста (100-250 см)
    """
    try:
        height = int(text.strip())
        if 100 <= height <= 250:
            return True, height
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_weight(text: str) -> Tuple[bool, float]:
    """
    Валидация веса (30-300 кг)
    """
    try:
        weight = float(text.strip().replace(',', '.'))
        if 30.0 <= weight <= 300.0:
            return True, round(weight, 1)
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0


def validate_sleep_hours(text: str) -> Tuple[bool, float]:
    """
    Валидация часов сна (0-24)
    """
    try:
        hours = float(text.strip().replace(',', '.'))
        if 0.0 <= hours <= 24.0:
            return True, round(hours, 1)
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0


def validate_training_time(text: str) -> Tuple[bool, int]:
    """
    Валидация времени тренировок в минутах (0-300)
    """
    try:
        minutes = int(text.strip())
        if 0 <= minutes <= 300:
            return True, minutes
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_training_days(text: str) -> Tuple[bool, int]:
    """
    Валидация дней тренировок в неделю (0-7)
    """
    try:
        days = int(text.strip())
        if 0 <= days <= 7:
            return True, days
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_date(text: str) -> Tuple[bool, any]:
    """
    Валидация даты в формате ДД.ММ.ГГГГ
    Возвращает datetime.date объект
    """
    try:
        from datetime import datetime
        date = datetime.strptime(text.strip(), "%d.%m.%Y").date()
        return True, date
    except (ValueError, TypeError):
        return False, None

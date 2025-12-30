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
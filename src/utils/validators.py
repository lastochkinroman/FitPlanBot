"""Валидаторы для данных анкеты"""

from datetime import datetime
from typing import Optional, Tuple


def validate_age(text: str) -> Tuple[bool, int]:
    """Валидация возраста (14-100)"""
    try:
        age = int(text.strip())
        return (14 <= age <= 100), age
    except:
        return False, 0


def validate_height(text: str) -> Tuple[bool, int]:
    """Валидация роста (100-250 см)"""
    try:
        height = int(text.strip())
        return (100 <= height <= 250), height
    except:
        return False, 0


def validate_weight(text: str) -> Tuple[bool, float]:
    """Валидация веса (30-300 кг)"""
    try:
        weight = float(text.strip().replace(",", "."))
        return (30.0 <= weight <= 300.0), round(weight, 1)
    except:
        return False, 0.0


def validate_sleep_hours(text: str) -> Tuple[bool, float]:
    """Валидация часов сна (0-24)"""
    try:
        hours = float(text.strip().replace(",", "."))
        return (0.0 <= hours <= 24.0), round(hours, 1)
    except:
        return False, 0.0


def validate_training_time(text: str) -> Tuple[bool, int]:
    """Валидация времени тренировок (0-300 минут)"""
    try:
        minutes = int(text.strip())
        return (0 <= minutes <= 300), minutes
    except:
        return False, 0


def validate_training_days(text: str) -> Tuple[bool, int]:
    """Валидация дней тренировок (0-7 дней)"""
    try:
        days = int(text.strip())
        return (0 <= days <= 7), days
    except:
        return False, 0


def validate_date(text: str) -> Tuple[bool, Optional[datetime.date]]:
    """Валидация даты формата ДД.ММ.ГГГГ"""
    try:
        date = datetime.strptime(text.strip(), "%d.%m.%Y").date()
        return True, date
    except:
        return False, None

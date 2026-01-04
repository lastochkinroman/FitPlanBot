"""Модели базы данных SQLAlchemy"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DECIMAL,
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# Базовый класс
Base = declarative_base()


def uuid_gen():
    """Генератор UUID"""
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    telegram_username = Column(String(64))
    first_name = Column(String(64))
    last_name = Column(String(64))
    phone_number = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Связи
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    daily_logs = relationship("UserDailyLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("age >= 14 AND age <= 100"),
        CheckConstraint("gender IN ('male', 'female', 'other')"),  # Исправлено
        CheckConstraint("height_cm BETWEEN 100 AND 250"),
        CheckConstraint("weight_kg BETWEEN 30 AND 300"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Основные данные
    age = Column(Integer)
    gender = Column(String(20))
    height_cm = Column(Integer)
    weight_kg = Column(DECIMAL(4, 1))
    target_weight_kg = Column(DECIMAL(4, 1))
    body_type = Column(String(50))

    # Цели и образ жизни
    goal = Column(String(50))
    lifestyle = Column(String(50))
    sleep_hours = Column(DECIMAL(3, 1))
    genetics_description = Column(Text)
    is_experienced_training = Column(Boolean)
    last_ideal_form_date = Column(Date)

    # Тренировки
    training_focus_area = Column(String(100))
    training_location = Column(String(50))
    training_time_minutes = Column(Integer)
    training_days_per_week = Column(Integer)
    preferred_training_type = Column(String(100))
    preferred_difficulty = Column(String(50))

    # Здоровье
    injuries_description = Column(Text)
    flexibility_level = Column(String(50))
    endurance_level = Column(String(50))

    # Метаданные
    profile_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    additional_data = Column(JSONB, default={})

    # Связи
    user = relationship("User", back_populates="profile")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'active', 'cancelled', 'expired')"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Статус
    status = Column(String(20), default="pending")
    activated_by_admin = Column(Boolean, default=False)
    activated_at = Column(DateTime(timezone=True))

    # Для платежей
    yookassa_payment_id = Column(String(255))
    yookassa_subscription_id = Column(String(255))
    amount = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="RUB")

    # Даты
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="subscriptions")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Целевые параметры
    target_goal = Column(JSONB)  # JSONB для PostgreSQL
    target_level = Column(JSONB)
    target_body_type = Column(JSONB)

    # Структура
    schedule = Column(JSONB, nullable=False)
    video_links = Column(JSONB, default={})

    # Метаданные
    is_active = Column(Boolean, default=True)
    created_by_admin = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Целевые параметры
    target_goal = Column(JSONB)
    calories_range = Column(JSONB)

    # Файлы
    pdf_file_path = Column(String(500))
    image_file_paths = Column(JSONB)

    # Метаданные
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserDailyLog(Base):
    __tablename__ = "user_daily_logs"
    __table_args__ = (CheckConstraint("workout_rating BETWEEN 1 AND 5"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Date, nullable=False, default=func.current_date)

    # Тренировки
    workout_completed = Column(Boolean, default=False)
    workout_rating = Column(Integer)
    workout_feedback = Column(Text)

    # Питание
    meal_plan_followed = Column(Boolean, default=False)
    meal_feedback = Column(Text)

    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="daily_logs")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'sent', 'failed', 'read')"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Контент
    type = Column(String(50), nullable=False)
    title = Column(String(200))
    message = Column(Text, nullable=False)

    # Статус
    status = Column(String(20), default="pending")

    # Время
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    user = relationship("User", back_populates="notifications")

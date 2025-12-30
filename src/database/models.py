import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, DECIMAL, Date, Text, JSON, BigInteger, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

# Импортируем Base из session.py
from src.database.session import Base

def uuid_gen():
    return str(uuid.uuid4())

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
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    daily_logs = relationship("UserDailyLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        CheckConstraint("age >= 14 AND age <= 100"),
        CheckConstraint("gender IN ('male', 'female'"),
        CheckConstraint("height_cm BETWEEN 100 AND 250"),
        CheckConstraint("weight_kg BETWEEN 30 AND 300"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
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
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    additional_data = Column(JSONB, default={})
    
    # Связи
    user = relationship("User", back_populates="profile")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'active', 'cancelled', 'expired')"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Статус подписки
    status = Column(String(20), default="pending")
    
    # Для MVP
    activated_by_admin = Column(Boolean, default=False)
    activated_at = Column(DateTime(timezone=True))
    
    # Для будущей интеграции с ЮKассой
    yookassa_payment_id = Column(String(255))
    yookassa_subscription_id = Column(String(255))
    amount = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="RUB")
    
    # Даты
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="subscriptions")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Целевые параметры
    target_goal = Column(JSON)  # Массив целей
    target_level = Column(JSON)  # Массив уровней
    target_body_type = Column(JSON)  # Массив типов телосложения
    
    # Структура
    schedule = Column(JSONB, nullable=False)  # { "day1": { упражнения }, "day2": ... }
    video_links = Column(JSONB, default={})
    
    # Метаданные
    is_active = Column(Boolean, default=True)
    created_by_admin = Column(UUID(as_uuid=True))  # ссылка на админа
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Целевые параметры
    target_goal = Column(JSON)  # Массив целей
    calories_range = Column(JSON)  # Массив [min, max]
    
    # Файлы
    pdf_file_path = Column(String(500))
    image_file_paths = Column(JSON)  # Массив путей
    
    # Метаданные
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class UserDailyLog(Base):
    __tablename__ = "user_daily_logs"
    __table_args__ = (
        CheckConstraint("workout_rating BETWEEN 1 AND 5"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow().date)
    
    # Тренировки
    workout_completed = Column(Boolean, default=False)
    workout_rating = Column(Integer)
    workout_feedback = Column(Text)
    
    # Питание
    meal_plan_followed = Column(Boolean, default=False)
    meal_feedback = Column(Text)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="daily_logs")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'sent', 'failed', 'read')"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_gen)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Контент
    type = Column(String(50), nullable=False)  # 'workout_reminder', 'meal_reminder', 'motivation'
    title = Column(String(200))
    message = Column(Text, nullable=False)
    
    # Статус
    status = Column(String(20), default="pending")
    
    # Время
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="notifications")
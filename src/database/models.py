import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional

from sqlalchemy import (
    ARRAY,
    BigInteger,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Аннотации для часто используемых типов
uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=func.now())
]


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    telegram_username: Mapped[Optional[str]] = mapped_column(String(64))
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_blocked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    # Связи
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_logs: Mapped[List["UserDailyLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid_pk]
    # Исправлено: ondelete (без подчеркивания)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    age: Mapped[Optional[int]]
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    height_cm: Mapped[Optional[int]]
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1))
    target_weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1))
    body_type: Mapped[Optional[str]] = mapped_column(String(50))
    goal: Mapped[Optional[str]] = mapped_column(String(50))
    lifestyle: Mapped[Optional[str]] = mapped_column(String(50))
    sleep_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1))
    genetics_description: Mapped[Optional[str]] = mapped_column(Text)
    is_experienced_training: Mapped[bool] = mapped_column(default=False)
    last_ideal_form_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    training_focus_area: Mapped[Optional[str]] = mapped_column(String(100))
    training_location: Mapped[Optional[str]] = mapped_column(String(50))
    training_time_minutes: Mapped[Optional[int]]
    training_days_per_week: Mapped[Optional[int]]
    preferred_training_type: Mapped[Optional[str]] = mapped_column(String(100))
    preferred_difficulty: Mapped[Optional[str]] = mapped_column(String(50))
    injuries_description: Mapped[Optional[str]] = mapped_column(Text)
    flexibility_level: Mapped[Optional[str]] = mapped_column(String(50))
    endurance_level: Mapped[Optional[str]] = mapped_column(String(50))
    profile_completed: Mapped[bool] = mapped_column(default=False, index=True)
    completed_at: Mapped[Optional[datetime]]
    updated_at: Mapped[updated_at]
    additional_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, server_default=text("'{}'")
    )

    user: Mapped["User"] = relationship(back_populates="profile")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid_pk]
    # Исправлено: ondelete
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    activated_by_admin: Mapped[bool] = mapped_column(default=False)
    activated_at: Mapped[Optional[datetime]]
    yookassa_payment_id: Mapped[Optional[str]] = mapped_column(String(255))
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    starts_at: Mapped[Optional[datetime]]
    ends_at: Mapped[Optional[datetime]] = mapped_column(index=True)
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_goal: Mapped[List[str]] = mapped_column(ARRAY(String(50)))
    target_level: Mapped[List[str]] = mapped_column(ARRAY(String(50)))
    schedule: Mapped[dict] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_at: Mapped[created_at]


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100))
    target_goal: Mapped[List[str]] = mapped_column(ARRAY(String(50)))
    calories_range: Mapped[List[int]] = mapped_column(ARRAY(BigInteger))
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]


class UserDailyLog(Base):
    __tablename__ = "user_daily_logs"

    id: Mapped[uuid_pk]
    # Исправлено: ondelete
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        server_default=func.current_date(), index=True
    )
    workout_completed: Mapped[bool] = mapped_column(default=False)
    workout_rating: Mapped[Optional[int]]
    meal_plan_followed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship(back_populates="daily_logs")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid_pk]
    # Исправлено: ondelete
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    scheduled_for: Mapped[datetime] = mapped_column(index=True)
    sent_at: Mapped[Optional[datetime]]
    created_at: Mapped[created_at]

    user: Mapped["User"] = relationship(back_populates="notifications")

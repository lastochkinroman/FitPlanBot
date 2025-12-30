from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncSession
from wtforms import TextAreaField

from src.database.models import User, UserProfile, Subscription, WorkoutPlan, MealPlan, UserDailyLog, Notification
from src.database.session import engine, async_session_maker
from src.database.repositories.subscription_repo import SubscriptionRepository

# Создаем FastAPI приложение
app = FastAPI(title="FitPlanBot Admin", version="1.0.0")

# Простая аутентификация по токену
security = HTTPBearer()
ADMIN_TOKEN = "admin_secret_token_12345"  # В проде использовать переменную окружения

async def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Создаем SQLAdmin
admin = Admin(app, engine)

# Модель администратора для пользователей
class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.telegram_id,
        User.telegram_username,
        User.first_name,
        User.last_name,
        User.is_active,
        User.is_blocked,
        User.created_at,
    ]
    column_details_list = [
        User.id,
        User.telegram_id,
        User.telegram_username,
        User.first_name,
        User.last_name,
        User.phone_number,
        User.email,
        User.is_active,
        User.is_blocked,
        User.created_at,
        User.updated_at,
    ]
    column_searchable_list = [User.telegram_username, User.first_name, User.last_name]
    column_sortable_list = [User.created_at, User.telegram_id]
    can_create = False  # Не позволяем создавать пользователей через админку
    can_delete = False  # Не позволяем удалять пользователей

# Модель администратора для профилей пользователей
class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [
        UserProfile.user_id,
        UserProfile.age,
        UserProfile.gender,
        UserProfile.height_cm,
        UserProfile.weight_kg,
        UserProfile.goal,
        UserProfile.profile_completed,
        UserProfile.completed_at,
    ]
    column_details_list = [
        UserProfile.id,
        UserProfile.user_id,
        UserProfile.age,
        UserProfile.gender,
        UserProfile.height_cm,
        UserProfile.weight_kg,
        UserProfile.target_weight_kg,
        UserProfile.body_type,
        UserProfile.goal,
        UserProfile.lifestyle,
        UserProfile.sleep_hours,
        UserProfile.genetics_description,
        UserProfile.is_experienced_training,
        UserProfile.last_ideal_form_date,
        UserProfile.training_focus_area,
        UserProfile.training_location,
        UserProfile.training_time_minutes,
        UserProfile.training_days_per_week,
        UserProfile.preferred_training_type,
        UserProfile.preferred_difficulty,
        UserProfile.injuries_description,
        UserProfile.flexibility_level,
        UserProfile.endurance_level,
        UserProfile.profile_completed,
        UserProfile.completed_at,
        UserProfile.updated_at,
    ]
    column_searchable_list = [UserProfile.goal, UserProfile.body_type]
    column_sortable_list = [UserProfile.completed_at, UserProfile.age]
    can_create = False
    can_delete = False

# Модель администратора для подписок
class SubscriptionAdmin(ModelView, model=Subscription):
    column_list = [
        Subscription.id,
        Subscription.user_id,
        Subscription.status,
        Subscription.activated_by_admin,
        Subscription.created_at,
        Subscription.starts_at,
        Subscription.ends_at,
    ]
    column_details_list = [
        Subscription.id,
        Subscription.user_id,
        Subscription.status,
        Subscription.activated_by_admin,
        Subscription.activated_at,
        Subscription.yookassa_payment_id,
        Subscription.yookassa_subscription_id,
        Subscription.amount,
        Subscription.currency,
        Subscription.starts_at,
        Subscription.ends_at,
        Subscription.created_at,
    ]
    column_searchable_list = [Subscription.status]
    column_sortable_list = [Subscription.created_at, Subscription.starts_at]
    can_create = False  # Подписки создаются через бота

    async def on_model_change(self, data, model, is_created, request):
        """Обработка изменений модели"""
        # Если статус меняется на 'active' ИЛИ activated_by_admin меняется на True, активируем подписку
        status_changed_to_active = data.get('status') == 'active' and model.status != 'active'
        admin_activated = data.get('activated_by_admin') is True and getattr(model, 'activated_by_admin', False) != True

        if status_changed_to_active or admin_activated:
            # Обновляем данные перед сохранением
            data['status'] = 'active'
            data['activated_by_admin'] = True
            # Устанавливаем даты активации
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            data['activated_at'] = now
            data['starts_at'] = now
            data['ends_at'] = now + timedelta(days=30)

        return await super().on_model_change(data, model, is_created, request)

# Модель администратора для планов тренировок
class WorkoutPlanAdmin(ModelView, model=WorkoutPlan):
    column_list = [
        WorkoutPlan.id,
        WorkoutPlan.name,
        WorkoutPlan.is_active,
        WorkoutPlan.created_at,
    ]
    column_details_list = [
        WorkoutPlan.id,
        WorkoutPlan.name,
        WorkoutPlan.description,
        WorkoutPlan.target_goal,
        WorkoutPlan.target_level,
        WorkoutPlan.target_body_type,
        WorkoutPlan.schedule,
        WorkoutPlan.video_links,
        WorkoutPlan.is_active,
        WorkoutPlan.created_by_admin,
        WorkoutPlan.created_at,
    ]
    column_searchable_list = [WorkoutPlan.name]
    column_sortable_list = [WorkoutPlan.created_at]

    # Настраиваем отображение JSON полей
    form_overrides = {
        'target_goal': TextAreaField,
        'target_level': TextAreaField,
        'target_body_type': TextAreaField,
        'schedule': TextAreaField,
        'video_links': TextAreaField,
    }

    column_labels = {
        'target_goal': 'Цели (JSON массив)',
        'target_level': 'Уровни сложности (JSON массив)',
        'target_body_type': 'Типы телосложения (JSON массив)',
        'schedule': 'Расписание (JSON объект)',
        'video_links': 'Видео ссылки (JSON объект)',
        'created_by_admin': 'Создано администратором',
    }

# Модель администратора для планов питания
class MealPlanAdmin(ModelView, model=MealPlan):
    column_list = [
        MealPlan.id,
        MealPlan.name,
        MealPlan.is_active,
        MealPlan.created_at,
    ]
    column_details_list = [
        MealPlan.id,
        MealPlan.name,
        MealPlan.description,
        MealPlan.target_goal,
        MealPlan.calories_range,
        MealPlan.pdf_file_path,
        MealPlan.image_file_paths,
        MealPlan.is_active,
        MealPlan.created_at,
    ]
    column_searchable_list = [MealPlan.name]
    column_sortable_list = [MealPlan.created_at]

    # Настраиваем отображение JSON полей
    form_overrides = {
        'target_goal': TextAreaField,
        'calories_range': TextAreaField,
        'image_file_paths': TextAreaField,
    }

    column_labels = {
        'target_goal': 'Цели (JSON массив)',
        'calories_range': 'Диапазон калорий (JSON массив)',
        'pdf_file_path': 'Путь к PDF файлу',
        'image_file_paths': 'Пути к изображениям (JSON массив)',
    }

# Модель администратора для логов активности
class UserDailyLogAdmin(ModelView, model=UserDailyLog):
    column_list = [
        UserDailyLog.id,
        UserDailyLog.user_id,
        UserDailyLog.date,
        UserDailyLog.workout_completed,
        UserDailyLog.meal_plan_followed,
    ]
    column_details_list = [
        UserDailyLog.id,
        UserDailyLog.user_id,
        UserDailyLog.date,
        UserDailyLog.workout_completed,
        UserDailyLog.workout_rating,
        UserDailyLog.workout_feedback,
        UserDailyLog.meal_plan_followed,
        UserDailyLog.meal_feedback,
        UserDailyLog.created_at,
    ]
    column_sortable_list = [UserDailyLog.date, UserDailyLog.created_at]
    can_create = False
    can_edit = False  # Логи только для чтения

# Модель администратора для уведомлений
class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.type,
        Notification.status,
        Notification.scheduled_for,
        Notification.sent_at,
    ]
    column_details_list = [
        Notification.id,
        Notification.user_id,
        Notification.type,
        Notification.title,
        Notification.message,
        Notification.status,
        Notification.scheduled_for,
        Notification.sent_at,
        Notification.created_at,
    ]
    column_searchable_list = [Notification.type, Notification.status]
    column_sortable_list = [Notification.scheduled_for, Notification.sent_at]
    can_create = False
    can_edit = False  # Уведомления только для чтения

# Регистрируем все модели в админке
admin.add_view(UserAdmin)
admin.add_view(UserProfileAdmin)
admin.add_view(SubscriptionAdmin)
admin.add_view(WorkoutPlanAdmin)
admin.add_view(MealPlanAdmin)
admin.add_view(UserDailyLogAdmin)
admin.add_view(NotificationAdmin)

# Маршрут для проверки работы API
@app.get("/")
async def root():
    return {"message": "FitPlanBot Admin API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

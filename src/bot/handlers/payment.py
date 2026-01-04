"""Хэндлеры для работы с подписками и платежами"""

import logging
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy import select

from src.bot.keyboards.main_menu import get_main_menu_kb
from src.bot.keyboards.subscription import get_subscription_keyboard
from src.database.models import Subscription, User
from src.database.session import async_session_maker

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("subscription"))
@router.message(F.text == "💳 Купить подписку")
async def subscription_info(message: types.Message):
    """
    Показывает информацию о подписке и кнопку для запроса активации

    Шаги 109-110: Хэндлер на кнопку "💳 Купить подписку"
    """
    async with async_session_maker() as session:
        # Проверяем существующую подписку
        stmt_user = select(User).where(User.telegram_id == message.from_user.id)
        user = (await session.execute(stmt_user)).scalar_one_or_none()

        if not user:
            await message.answer(
                "❌ Сначала зарегистрируйтесь с помощью команды /start",
                reply_markup=get_main_menu_kb(),
            )
            return

        stmt_sub = (
            select(Subscription)
            .where(Subscription.user_id == user.id)
            .order_by(Subscription.created_at.desc())
        )

        subscription = (await session.execute(stmt_sub)).scalar_one_or_none()

    if subscription:
        # Показываем статус существующей подписки
        status_map = {
            "pending": "⏳ Ожидает активации",
            "active": "✅ Активна",
            "cancelled": "❌ Отменена",
            "expired": "⏰ Истекла",
        }

        status_text = status_map.get(subscription.status, subscription.status)

        response = (
            f"💳 <b>Ваша подписка</b>\n\n"
            f"📊 <b>Статус:</b> {status_text}\n"
            f"📅 <b>Создана:</b> {subscription.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        )

        if subscription.starts_at and subscription.ends_at:
            response += (
                f"▶️ <b>Начало:</b> {subscription.starts_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"⏹️ <b>Окончание:</b> {subscription.ends_at.strftime('%d.%m.%Y %H:%M')}\n"
            )

        if subscription.status == "pending":
            response += (
                f"\nℹ️ <b>Администратор рассмотрит вашу заявку в течение 24 часов.</b>\n"
                f"После активации вы получите доступ ко всем функциям бота."
            )
            await message.answer(
                response, parse_mode="HTML", reply_markup=get_main_menu_kb()
            )
            return
        elif subscription.status == "active":
            response += (
                f"\n🎉 <b>Ваша подписка активна!</b>\n"
                f"Теперь вам доступны все функции бота:\n"
                f"• 🏋️ Персональные планы тренировок\n"
                f"• 🍎 Индивидуальное питание\n"
                f"• 🔔 Умные напоминания\n"
                f"• 📊 Отслеживание прогресса"
            )
            await message.answer(
                response, parse_mode="HTML", reply_markup=get_main_menu_kb()
            )
            return

    # Если подписки нет или она не активна
    await message.answer(
        "💳 <b>Подписка FitPlanBot</b>\n\n"
        "🔓 <b>Получите полный доступ ко всем функциям:</b>\n"
        "✅ Персональные планы тренировок\n"
        "✅ Индивидуальное питание\n"
        "✅ Умные напоминания\n"
        "✅ Отслеживание прогресса\n"
        "✅ Поддержка 24/7\n\n"
        "🎯 <b>Как это работает:</b>\n"
        "1. Запросите активацию подписки\n"
        "2. Администратор активирует её вручную\n"
        "3. Получите доступ на 30 дней\n\n"
        "<i>После активации мы свяжемся с вами для уточнения деталей</i>",
        parse_mode="HTML",
        reply_markup=get_subscription_keyboard(),
    )


@router.callback_query(F.data == "request_subscription")
async def request_subscription(callback: types.CallbackQuery):
    """
    Обработка нажатия кнопки "Запросить активацию"

    Шаг 112: Создание записи в subscriptions со статусом pending
    """
    async with async_session_maker() as session:
        # Находим пользователя
        stmt_user = select(User).where(User.telegram_id == callback.from_user.id)
        user = (await session.execute(stmt_user)).scalar_one_or_none()

        if not user:
            await callback.answer("❌ Сначала зарегистрируйтесь через /start")
            return

        # Проверяем существующую pending подписку
        stmt_pending = select(Subscription).where(
            Subscription.user_id == user.id, Subscription.status == "pending"
        )
        existing_pending = (await session.execute(stmt_pending)).scalar_one_or_none()

        if existing_pending:
            await callback.answer(
                "⏳ Заявка уже отправлена и ожидает рассмотрения", show_alert=True
            )
            return

        # Создаем новую подписку со статусом pending
        subscription = Subscription(
            user_id=user.id,
            status="pending",
            activated_by_admin=False,
            created_at=datetime.utcnow(),
        )

        session.add(subscription)
        await session.commit()

        logger.info(f"Created pending subscription for user {user.id}")

    # Обновляем сообщение
    await callback.message.edit_text(
        "✅ <b>Заявка отправлена!</b>\n\n"
        "📋 <b>Ваша заявка на подписку принята.</b>\n\n"
        "📝 <b>Что дальше:</b>\n"
        "1. Администратор получит уведомление\n"
        "2. Ваша заявка будет рассмотрена в течение 24 часов\n"
        "3. После активации вы получите доступ ко всем функциям\n\n"
        "🆔 <b>Номер заявки:</b> #{subscription_id}\n".format(
            subscription_id=str(subscription.id)[:8].upper()
        ),
        parse_mode="HTML",
    )

    await callback.answer("Заявка успешно отправлена!")


@router.callback_query(F.data == "cancel_subscription_request")
async def cancel_subscription_request(callback: types.CallbackQuery):
    """Отмена запроса на подписку"""
    await callback.message.edit_text(
        "❌ <b>Запрос на подписку отменен</b>\n\n"
        "Если передумаете, вы всегда можете запросить подписку снова.",
        parse_mode="HTML",
    )
    await callback.answer("Запрос отменен")


@router.message(Command("my_subscription"))
async def my_subscription_command(message: types.Message):
    """Команда для просмотра текущей подписки"""
    await subscription_info(message)

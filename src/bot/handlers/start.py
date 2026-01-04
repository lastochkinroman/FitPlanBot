"""Хэндлеры для стартовых команд бота"""

import logging

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from sqlalchemy import select

from src.bot.keyboards.main_menu import get_main_menu_kb
from src.database.models import User
from src.database.repositories.user_repo import UserRepository
from src.database.session import async_session_maker

router = Router()
logger = logging.getLogger(__name__)


async def get_or_create_user(telegram_user: types.User) -> User:
    """
    Получает существующего пользователя или создает нового

    Args:
        telegram_user: Пользователь из Telegram

    Returns:
        User: Объект пользователя из базы данных
    """
    async with async_session_maker() as session:
        repo = UserRepository(session)

        # Пытаемся найти пользователя
        user = await repo.get_by_telegram_id(telegram_user.id)

        if user:
            # Обновляем информацию о пользователе, если она изменилась
            update_data = {}
            if user.first_name != telegram_user.first_name:
                update_data["first_name"] = telegram_user.first_name
            if user.last_name != telegram_user.last_name:
                update_data["last_name"] = telegram_user.last_name
            if user.telegram_username != telegram_user.username:
                update_data["telegram_username"] = telegram_user.username

            if update_data:
                user = await repo.update(user.id, **update_data)
                logger.info(f"Updated user {telegram_user.id}: {update_data}")

            logger.info(f"User found in DB: {telegram_user.id}")
            return user

        # Создаем нового пользователя
        user_data = {
            "telegram_id": telegram_user.id,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "telegram_username": telegram_user.username,
            "is_active": True,
        }

        user = await repo.create(**user_data)
        logger.info(f"Created new user in DB: {telegram_user.id}")
        return user


@router.message(Command("start"))
async def start_command(message: types.Message, command: CommandObject | None = None):
    """
    Обработчик команды /start

    Args:
        message: Сообщение от пользователя
        command: Объект команды с аргументами
    """
    user = message.from_user

    # Сохраняем/обновляем пользователя в базе данных
    db_user = await get_or_create_user(user)

    # Проверяем наличие реферального кода
    referral_source = None
    if command and command.args:
        referral_source = command.args
        logger.info(f"User {user.id} came from referral: {referral_source}")
        # Здесь можно добавить логику обработки рефералов

    # Формируем приветственное сообщение
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — <b>FitPlanBot</b>, твой персональный помощник по тренировкам и питанию.\n\n"
        "✨ <b>Что я умею:</b>\n"
        "• 🏋️‍♂️ Создавать <b>индивидуальные планы тренировок</b>\n"
        "• 🍎 Подбирать <b>рацион питания</b>\n"
        "• 🔔 Напоминать о тренировках\n"
        "• 📊 Отслеживать твой прогресс\n\n"
        "🚀 <b>Как начать:</b>\n"
        "1. 📝 <b>Заполни анкету</b> (5 минут)\n"
        "2. 💳 <b>Активируй подписку</b> для доступа\n"
        "3. 🎯 <b>Получи персональный план</b>\n\n"
        "📅 <b>Ты с нами с:</b> {created_date}".format(
            created_date=db_user.created_at.strftime("%d.%m.%Y")
        )
    )

    # Добавляем реферальную информацию, если есть
    if referral_source:
        welcome_text += f"\n\n🔗 <b>Приглашение от:</b> {referral_source}"

    await message.answer(
        text=welcome_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("help"))
async def help_command(message: types.Message):
    """
    Обработчик команды /help

    Args:
        message: Сообщение от пользователя
    """
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start — начать работу с ботом\n"
        "/profile — посмотреть профиль\n"
        "/help — показать это сообщение\n"
        "/cancel — отменить текущее действие\n\n"
        "<b>Планы и настройки:</b>\n"
        "/plan — получить план тренировок\n"
        "/nutrition — план питания\n"
        "/settings — настройки\n"
        "/subscription — информация о подписке\n\n"
        "<b>Профиль:</b>\n"
        "/me — посмотреть профиль (как /profile)\n"
        "/stats — статистика профиля\n"
        "/reset — сбросить анкету\n\n"
        "📱 <b>Или используй кнопки меню:</b>\n"
        "• <b>📝 Заполнить анкету</b> — создать/изменить профиль\n"
        "• <b>👤 Мой профиль</b> — посмотреть профиль\n"
        "• <b>🏋️ Мой план</b> — получить тренировочный план\n"
        "• <b>🍎 Питание</b> — получить план питания\n"
        "• <b>⚙️ Настройки</b> — настройки бота\n"
        "• <b>💳 Купить подписку</b> — активировать полный доступ\n\n"
        "❓ <b>Нужна помощь?</b>\n"
        "Если у вас возникли проблемы или вопросы, "
        "обратитесь к администратору @admin_username"
    )

    await message.answer(
        text=help_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("cancel"))
async def cancel_command(message: types.Message):
    """
    Обработчик команды /cancel

    Args:
        message: Сообщение от пользователя
    """
    await message.answer(
        text="✅ Текущее действие отменено. Вы можете начать заново.",
        reply_markup=get_main_menu_kb(),
    )


@router.message(Command("about"))
async def about_command(message: types.Message):
    """
    Обработчик команды /about

    Args:
        message: Сообщение от пользователя
    """
    about_text = (
        "🤖 <b>FitPlanBot</b>\n\n"
        "Персональный бот для тренировок и питания.\n\n"
        "<b>Версия:</b> 1.0.0 (MVP)\n"
        "<b>Разработчик:</b> FitPlanBot Team\n"
        "<b>Контакты:</b> @admin_username\n\n"
        "<b>Функции:</b>\n"
        "✅ Индивидуальные планы тренировок\n"
        "✅ Персональное питание\n"
        "✅ Умные напоминания\n"
        "✅ Отслеживание прогресса\n"
        "✅ Поддержка нескольких языков\n\n"
        "<b>Технологии:</b>\n"
        "• Python 3.11+\n"
        "• Aiogram 3.x\n"
        "• PostgreSQL\n"
        "• Redis\n\n"
        "🌟 <b>Мы в разработке!</b>\n"
        "Постепенно добавляем новые функции. "
        "Следите за обновлениями!"
    )

    await message.answer(
        text=about_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("version"))
async def version_command(message: types.Message):
    """
    Обработчик команды /version

    Args:
        message: Сообщение от пользователя
    """
    version_info = (
        "📱 <b>FitPlanBot Version Info</b>\n\n"
        "<b>Версия:</b> 1.0.0\n"
        "<b>Статус:</b> MVP (Minimum Viable Product)\n"
        "<b>Дата релиза:</b> 01.01.2024\n"
        "<b>Обновление:</b> Последнее обновление 01.01.2024\n\n"
        "<b>Текущие функции:</b>\n"
        "✅ Регистрация пользователей\n"
        "✅ Заполнение анкеты (24 вопроса)\n"
        "✅ Просмотр профиля\n"
        "✅ Система подписок (админ-активация)\n"
        "✅ Админ-панель\n\n"
        "<b>В разработке:</b>\n"
        "🔄 Подбор планов тренировок\n"
        "🔄 Подбор планов питания\n"
        "🔄 Система уведомлений\n"
        "🔄 Отслеживание прогресса\n\n"
        "<b>Планируется:</b>\n"
        "⏳ Интеграция с ЮKassa\n"
        "⏳ Мобильное приложение\n"
        "⏳ Расширенная аналитика"
    )

    await message.answer(
        text=version_info, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.message(Command("status"))
async def status_command(message: types.Message):
    """
    Проверка статуса бота и пользователя

    Args:
        message: Сообщение от пользователя
    """
    user = message.from_user

    async with async_session_maker() as session:
        repo = UserRepository(session)
        db_user = await repo.get_by_telegram_id(user.id)

        if not db_user:
            status_text = (
                "🔴 <b>Статус:</b> Не зарегистрирован\n"
                "➡️ Используйте /start для регистрации"
            )
        else:
            # Проверяем подписку (заглушка - будет в будущем)
            from src.database.repositories.subscription_repo import (
                SubscriptionRepository,
            )

            sub_repo = SubscriptionRepository(session)
            subscription = await sub_repo.get_active_subscription(db_user.id)

            subscription_status = "✅ Активна" if subscription else "❌ Не активна"

            status_text = (
                f"🟢 <b>Статус:</b> Зарегистрирован\n\n"
                f"<b>Пользователь:</b> {db_user.first_name}\n"
                f"<b>ID:</b> {db_user.telegram_id}\n"
                f"<b>Регистрация:</b> {db_user.created_at.strftime('%d.%m.%Y')}\n"
                f"<b>Подписка:</b> {subscription_status}\n"
                f"<b>Активен:</b> {'✅ Да' if db_user.is_active else '❌ Нет'}\n"
                f"<b>Заблокирован:</b> {'❌ Да' if db_user.is_blocked else '✅ Нет'}\n\n"
                "<b>Бот работает в штатном режиме</b> ✅"
            )

    await message.answer(
        text=status_text, parse_mode="HTML", reply_markup=get_main_menu_kb()
    )

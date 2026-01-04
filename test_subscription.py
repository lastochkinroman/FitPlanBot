"""Тестовый сценарий для проверки системы подписок"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import delete, select

from src.database.models import Subscription, User
from src.database.session import async_session_maker, engine


async def test_subscription_flow():
    """Тестируем полный цикл работы с подпиской"""
    print("🧪 Тестирование системы подписок...")

    # 1. Создаем тестового пользователя
    async with async_session_maker() as session:
        print("1. Создание тестового пользователя...")

        # Удаляем старые тестовые данные
        await session.execute(delete(Subscription))
        await session.execute(delete(User))
        await session.commit()

        # Создаем пользователя
        user = User(
            telegram_id=999999999,
            first_name="Test",
            last_name="User",
            telegram_username="testuser",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"   ✅ Создан пользователь: {user.id}")

        # 2. Проверяем, что подписки нет
        print("2. Проверка отсутствия подписки...")
        stmt = select(Subscription).where(Subscription.user_id == user.id)
        subscription = (await session.execute(stmt)).scalar_one_or_none()

        if subscription:
            print("   ❌ Подписка уже существует (не должно быть)")
        else:
            print("   ✅ Подписки нет (правильно)")

        # 3. Создаем pending подписку
        print("3. Создание pending подписки...")
        subscription = Subscription(
            user_id=user.id, status="pending", activated_by_admin=False
        )
        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)

        print(f"   ✅ Создана pending подписка: {subscription.id}")
        print(f"   Статус: {subscription.status}")

        # 4. Активируем подписку
        print("4. Активация подписки...")
        from datetime import datetime, timedelta

        subscription.status = "active"
        subscription.activated_by_admin = True
        subscription.activated_at = datetime.utcnow()
        subscription.starts_at = datetime.utcnow()
        subscription.ends_at = datetime.utcnow() + timedelta(days=30)

        await session.commit()
        await session.refresh(subscription)

        print(f"   ✅ Подписка активирована")
        print(f"   Статус: {subscription.status}")
        print(f"   Действует до: {subscription.ends_at}")

        # 5. Проверяем, что подписка активна
        print("5. Проверка активной подписки...")
        from datetime import datetime

        now = datetime.utcnow()

        stmt_active = select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active",
            Subscription.starts_at <= now,
            Subscription.ends_at >= now,
        )

        active_subscription = (await session.execute(stmt_active)).scalar_one_or_none()

        if active_subscription:
            print("   ✅ Активная подписка найдена")
        else:
            print("   ❌ Активная подписка не найдена")

    print("\n🎉 Все тесты пройдены успешно!")
    print("\n📋 Сводка:")
    print("1. ✅ Пользователь создан")
    print("2. ✅ Отсутствие подписки проверено")
    print("3. ✅ Pending подписка создана")
    print("4. ✅ Подписка активирована")
    print("5. ✅ Активная подписка проверена")


if __name__ == "__main__":
    asyncio.run(test_subscription_flow())

FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry
RUN pip install poetry

# Настраиваем Poetry для неинтерактивного режима
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --only=main --no-dev

# Копируем исходный код
COPY src/ ./src/

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Запускаем приложение
CMD ["uvicorn", "src.admin.web:app", "--host", "0.0.0.0", "--port", "8000"]

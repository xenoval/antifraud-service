FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY pyproject.toml ./
COPY app ./app

# Устанавливаем uv и зависимости
RUN pip install uv && \
    uv pip install --system -e .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

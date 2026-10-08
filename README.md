# Anti-Fraud Service API

Микросервис для проверки клиентов на мошенничество с кэшированием в Redis и мониторингом через Prometheus+Grafana.

## Быстрый старт

```bash
# 1. Запуск всех сервисов
docker compose up --build

# 2. Только приложение + Redis
docker compose up antifraud-service redis

# 3. С мониторингом
docker compose -f docker-compose.yml -f docker-compose.grafana.yml up
```

## API

### Основные эндпоинты:
- `GET /` - информация о сервисе
- `GET /health` - health check
- `GET /ready` - проверка зависимостей
- `POST /check` - **проверка на мошенничество**
- `GET /metrics` - Prometheus метрики

### Пример запроса:
```bash
curl -X POST "http://localhost:8000/check" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "15.01.1990",
    "phone_number": "+79161234567",
    "loans_history": [{
      "loan_amount": 10000.0,
      "loan_date": "15.01.2023",
      "is_closed": true
    }]
  }'
```

### Ответы /check
Эндпоинт всегда возвращает 200 OK, если запрос валиден, — независимо от результата проверки. Решение о пропуске или отказе закодировано в теле ответа (result), а не в HTTP-статусе.

## Мониторинг

| Сервис | URL | Порт |
|--------|-----|------|
| Приложение | http://localhost:8000 | 8000 |
| Документация | http://localhost:8000/docs | 8000 |
| Prometheus | http://localhost:9090 | 9090 |
| Grafana | http://localhost:3000 | 3000 |

**Логин в Grafana:** admin / значение переменной GRAFANA_ADMIN_PASSWORD из .env.

## Тестирование

```bash
# Запуск тестов
pytest tests/ -v

# С покрытием кода
pytest --cov=app --cov-report=html tests/
```

## Структура

```
antifraud-service/
├── app/
│   ├── __init__.py            
│   ├── config.py              # Конфигурация приложения
│   ├── healthz.py             # Эндпоинт проверки работоспособности сервиса (health checks)
│   ├── logger.py              # Настройка логирования
│   ├── logic.py               # Бизнес-логика приложения
│   ├── main.py                # Точка входа приложения
│   ├── metrics.py             # Метрики Prometheus для мониторинга
│   ├── redis_client.py        # Клиент для подключения к Redis
│   └── schemas.py             # Pydantic-схемы
├── tests/
│   ├── __init__.py            
│   └── test_main.py           # Тесты для основного функционала приложения
├── .dockerignore              # Исключения файлов при сборке Docker-образа
├── .env.example               # Пример файла с переменными окружения
├── .gitignore                 # Исключения файлов для Git
├── .python-version            # Версия Python
├── Dockerfile                 # Инструкции для сборки Docker-образа приложения
├── README.md                  
├── docker-compose.grafana.yml # Docker Compose для запуска Grafana
├── docker-compose.yml         # Основной Docker Compose
├── prometheus.yml             # Конфигурация Prometheus для сбора метрик
└── pyproject.toml             # Метаданные проекта и зависимости
```

## Бизнес-логика

Проверяет:
1. **Телефон** - начинается с +7 или 8
2. **Возраст** - старше 18 лет
3. **Займы** - нет активных (не закрытых) займов

**Результаты кэшируются в Redis на 1 час.**

## Зависимости

Установка:
```bash
pip install -e .
```

Основные зависимости:
- FastAPI, Pydantic, Redis
- Prometheus-client, Uvicorn
- Pytest (для разработки)

## Конфигурация

Скопируйте `.env.example` в `.env`:
```env
REDIS_HOST=redis
REDIS_PORT=6379
APP_PORT=8000
LOG_LEVEL=INFO
```

---

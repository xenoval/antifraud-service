# Anti-Fraud Service API

Микросервис для проверки клиентов на мошенничество с кэшированием в Redis и мониторингом через Prometheus+Grafana.

## Быстрый старт

```bash
# 1. Запуск всех сервисов
docker-compose up --build

# 2. Только приложение + Redis
docker-compose up app redis

# 3. С мониторингом
docker-compose -f docker-compose.yml -f docker-compose.grafana.yml up
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

## Мониторинг

| Сервис | URL | Порт |
|--------|-----|------|
| Приложение | http://localhost:8000 | 8000 |
| Документация | http://localhost:8000/docs | 8000 |
| Prometheus | http://localhost:9090 | 9090 |
| Grafana | http://localhost:3000 | 3000 |

**Логин в Grafana:** admin / admin123

## Тестирование

```bash
# Запуск тестов
pytest tests/ -v

# С покрытием кода
pytest --cov=app --cov-report=html tests/
```

## Структура

```
test_app/
├── app/                    # Код приложения
│   ├── main.py            # FastAPI приложение
│   ├── logic.py           # Бизнес-логика проверок
│   ├── redis_client.py    # Redis кэширование
│   └── schemas.py         # Pydantic схемы
├── tests/                 # Тесты
├── docker-compose.yml     # Docker конфигурация
├── Dockerfile            # Образ приложения
└── pyproject.toml        # Зависимости
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

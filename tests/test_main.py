from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _fmt(d: date) -> str:
    """Формат даты, который ждёт AntifraudRequest: dd.mm.yyyy"""
    return d.strftime("%d.%m.%Y")


def _birth_date_years_ago(years: int, *, days_shift: int = 0) -> str:
    """
    Дата рождения ровно `years` лет назад (с поправкой на days_shift).
    Гарантирует, что возраст на сегодня — ровно `years` (или `years` ± сдвиг).
    """
    today = date.today()
    try:
        d = today.replace(year=today.year - years)
    except ValueError:
        # 29 февраля в невисокосный год
        d = today.replace(year=today.year - years, day=28)
    return _fmt(d + timedelta(days=days_shift))


def test_check_fraud_success():
    """Тест успешной проверки"""
    data = {
        "birth_date": _birth_date_years_ago(40),  # заведомо взрослый
        "phone_number": "+79235648563",
        "loans_history": [{"loan_amount": 10000, "loan_date": "22.10.2023", "is_closed": True}],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 200
    result = response.json()

    assert result["result"]
    assert result["stop_factors"] == []


def test_check_fraud_young_age():
    """Тест: клиент младше 18 лет"""
    data = {
        "birth_date": _birth_date_years_ago(10),  # ровно 10 лет — точно < 18
        "phone_number": "+79235648563",
        "loans_history": [],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 200
    result = response.json()

    assert not result["result"]
    assert "Person is younger than 18" in result["stop_factors"]


def test_check_fraud_wrong_phone():
    """Тест: неправильный номер телефона"""
    data = {
        "birth_date": _birth_date_years_ago(40),
        "phone_number": "99235648563",  # Не начинается с +7 или 8
        "loans_history": [],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 200
    result = response.json()

    assert not result["result"]
    assert "Invalid phone number format" in result["stop_factors"]


def test_check_fraud_unclosed_loan():
    """Тест: есть незакрытый займ"""
    data = {
        "birth_date": _birth_date_years_ago(40),
        "phone_number": "+79235648563",
        "loans_history": [
            {
                "loan_amount": 10000,
                "loan_date": "22.10.2023",
                "is_closed": False,  # Незакрытый!
            }
        ],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 200
    result = response.json()

    assert not result["result"]
    assert "Not a closed loan" in result["stop_factors"]


def test_check_fraud_invalid_birth_date():
    """Тест: дата рождения в неверном формате → 422"""
    data = {
        "birth_date": "2010-08-22",  # ISO вместо dd.mm.yyyy
        "phone_number": "+79235648563",
        "loans_history": [],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 422


def test_check_fraud_missing_birth_date():
    """Тест: не передано обязательное поле birth_date → 422"""
    data = {
        # "birth_date" отсутствует
        "phone_number": "+79235648563",
        "loans_history": [],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 422


def test_check_fraud_all_stop_factors():
    """Тест: все стоп-факторы сразу"""
    data = {
        "birth_date": _birth_date_years_ago(10),  # младше 18
        "phone_number": "99161234567",  # ← добавлена запятая
        "loans_history": [
            {
                "loan_amount": 10000,
                "loan_date": "22.10.2023",
                "is_closed": False,  # незакрытый займ
            }
        ],
    }

    response = client.post("/check", json=data)

    assert response.status_code == 200
    result = response.json()

    assert not result["result"]
    # все три фактора должны быть в ответе (порядок — как в logic.py)
    assert result["stop_factors"] == [
        "Invalid phone number format",
        "Person is younger than 18",
        "Not a closed loan",
    ]


def test_check_fraud_cached_result(fake_redis):
    """Два одинаковых запроса: второй отдаётся из кэша"""
    data = {
        "birth_date": _birth_date_years_ago(10),  # младше 18 → отказ
        "phone_number": "+79235648563",
        "loans_history": [],
    }

    first = client.post("/check", json=data)
    second = client.post("/check", json=data)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()

    # ключ в кэше один и значение записано
    assert len(fake_redis.store) == 1


def test_health_body():
    """Тест: Жив ли?:)"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "anti-fraud"}

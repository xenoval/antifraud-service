from datetime import date, datetime

from app.logger import logger
from app.redis_client import redis_client
from app.schemas import AntifraudRequest, AntifraudResponse


def calculate_age(birthdate_str: str, today: date | None = None) -> int:
    birthdate = datetime.strptime(birthdate_str, "%d.%m.%Y").date()
    today = today or date.today()

    had_birthday = (today.month, today.day) >= (birthdate.month, birthdate.day)
    age = today.year - birthdate.year - (0 if had_birthday else 1)
    return age


def check_antifraud_logic(request: AntifraudRequest) -> AntifraudResponse:
    stop_factors = []

    # Проверка 1: Телефон начинается с +7 или 8?
    if not (request.phone_number.startswith("+7") or request.phone_number.startswith("8")):
        stop_factors.append("Invalid phone number format")

    # Проверка 2: Возраст меньше 18 лет?
    if calculate_age(request.birth_date) < 18:
        stop_factors.append("Person is younger than 18")

    # Проверка 3: Есть ли незакрытые займы?
    for loan in request.loans_history:
        if not loan.is_closed:
            stop_factors.append("Not a closed loan")
            break

    result = len(stop_factors) == 0  # True если нет стоп-факторов
    return AntifraudResponse(stop_factors=stop_factors, result=result)


def check_antifraud(request: AntifraudRequest) -> AntifraudResponse:
    request_dict = request.model_dump()
    cache_key = redis_client.generate_key(request_dict)

    logger.info(f"Проверка antifraud: {request.phone_number}")

    cached_result = redis_client.get_cached_result(cache_key)
    if cached_result:
        logger.info(f"Результат из кэша для {request.phone_number}")
        return AntifraudResponse(**cached_result)

    logger.debug(f"Выполняем проверки для {request.phone_number}")
    result = check_antifraud_logic(request)

    redis_client.set_cached_result(cache_key, result.model_dump())
    status = "УСПЕХ" if result.result else "ОТКАЗ"
    logger.info(f"Проверка завершена: {status} для {request.phone_number}")

    return result

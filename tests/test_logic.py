from datetime import date

import pytest

from app.logic import calculate_age, check_antifraud_logic
from app.schemas import AntifraudRequest, Loan


@pytest.mark.parametrize(
    "birth, today, expected",
    [
        ("15.01.2008", date(2026, 1, 15), 18),  # день рождения сегодня
        ("16.01.2008", date(2026, 1, 15), 17),  # не хватает одного дня
        ("29.02.2008", date(2026, 2, 28), 17),  # 29 февраля
        ("29.02.2008", date(2026, 3, 1), 18),
    ],
)
def test_calculate_age(birth, today, expected):
    assert calculate_age(birth, today) == expected


@pytest.mark.parametrize(
    "phone, expect_invalid",
    [
        pytest.param("+79161234567", False, id="plus7-916"),
        pytest.param("89161234567", False, id="eight-916"),
        pytest.param("99161234567", True, id="no-prefix-916"),
        pytest.param("", True, id="empty"),
    ],
)
def test_phone_format(phone, expect_invalid):
    request = AntifraudRequest(
        phone_number=phone,
        birth_date="01.01.1990",  # заведомо > 18 лет
        loans_history=[],  # нет незакрытых займов
    )
    response = check_antifraud_logic(request)
    has_factor = "Invalid phone number format" in response.stop_factors
    assert has_factor is expect_invalid


@pytest.mark.parametrize(
    "loans, expect_invalid",
    [
        pytest.param([], False, id="empty"),
        pytest.param(
            [Loan(loan_amount=10000, loan_date="01.01.2020", is_closed=True)],
            False,
            id="everything-closed",
        ),
        pytest.param(
            [
                Loan(loan_amount=10000, loan_date="01.01.2020", is_closed=True),
                Loan(loan_amount=5000, loan_date="01.06.2021", is_closed=False),
                Loan(loan_amount=2000, loan_date="01.09.2022", is_closed=True),
            ],
            True,
            id="one-open-among-closed-ones",
        ),
        pytest.param(
            [
                Loan(loan_amount=10000, loan_date="01.01.2020", is_closed=False),
                Loan(loan_amount=5000, loan_date="01.06.2021", is_closed=False),
            ],
            True,
            id="several-open-ones-among-closed-ones",
        ),
    ],
)
def test_loans(loans, expect_invalid):
    request = AntifraudRequest(
        phone_number="+79160236868",
        birth_date="01.01.1990",
        loans_history=loans,
    )
    response = check_antifraud_logic(request)
    has_factor = "Not a closed loan" in response.stop_factors
    assert has_factor is expect_invalid

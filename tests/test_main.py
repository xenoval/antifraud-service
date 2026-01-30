import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_check_fraud_success():
    """Тест успешной проверки"""
    data = {
        "birth_date": "22.08.1977",
        "phone_number": "+79235648563",
        "loans_history": [
            {
                "amount": 10000,
                "loan_data": "22.10.2023",
                "is_closed": True
            }
        ]
    }
    
    response = client.post("/check", json=data)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["result"] == True
    assert result["stop_factors"] == []

def test_check_fraud_young_age():
    # Тест: клиент младше 18 лет
    data = {
        "birth_date": "22.08.2010",  # Младше 18
        "phone_number": "+79235648563",
        "loans_history": []
    }
    
    response = client.post("/check", json=data)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["result"] == False
    assert "Person is younger than 18" in result["stop_factors"]

def test_check_fraud_wrong_phone():
    # Тест: неправильный номер телефона
    data = {
        "birth_date": "22.08.1977",
        "phone_number": "99235648563",  # Не начинается с +7 или 8
        "loans_history": []
    }
    
    response = client.post("/check", json=data)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["result"] == False
    assert "Invalid phone number format" in result["stop_factors"]

def test_check_fraud_unclosed_loan():
    # Тест: есть незакрытый займ
    data = {
        "birth_date": "22.08.1977",
        "phone_number": "+79235648563",
        "loans_history": [
            {
                "amount": 10000,
                "loan_data": "22.10.2023",
                "is_closed": False  # Незакрытый!
            }
        ]
    }
    
    response = client.post("/check", json=data)
    
    assert response.status_code == 200
    result = response.json()
    
    assert result["result"] == False
    assert "Not a closed loan" in result["stop_factors"]
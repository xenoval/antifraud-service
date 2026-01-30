from pydantic import BaseModel, field_validator
from datetime import datetime


class Loan(BaseModel):
    amount: int
    loan_data: str
    # В документации именно loan_data
    is_closed: bool

    @field_validator('loan_data')
    def validate_loan_data(cls, v):
        try:
            datetime.strptime(v, '%d.%m.%Y')
            return v
        except ValueError:
            raise ValueError('Date must be in format dd.mm.yyyy')

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <=0:
            raise ValueError('Amount must be positive')
        return v

class AntifraudRequest(BaseModel):
    birth_date: str
    phone_number: str
    loans_history: list[Loan]

    @field_validator('birth_date')
    def validate_birth_date(cls, v):
        try:
            datetime.strptime(v, '%d.%m.%Y')
            return v
        except ValueError:
            raise ValueError('Date must be in format dd.mm.yyyy')

class AntifraudResponse(BaseModel):
    stop_factors: list[str]
    result: bool

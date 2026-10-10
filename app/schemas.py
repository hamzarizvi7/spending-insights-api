import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    merchant: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    date: datetime.date

    @field_validator("date")
    @classmethod
    def not_in_future(cls, v):
        if v > datetime.date.today():
            raise ValueError("date cannot be in the future")
        return v


class TransactionOut(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
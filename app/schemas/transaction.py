from datetime import datetime, date as date_type
from pydantic import BaseModel, Field, ConfigDict


class TransactionBase(BaseModel):
    account_id: int
    category_id: int | None = None
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    description: str | None = None
    date: date_type | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    amount: float | None = Field(None, gt=0)
    type: str | None = Field(None, pattern="^(income|expense)$")
    description: str | None = None
    date: date_type | None = None


class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    category_name: str | None = None
    account_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
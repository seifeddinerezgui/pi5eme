# app/schemas/transaction.py
from pydantic import BaseModel
from datetime import datetime

class TransactionBase(BaseModel):
    symbol: str
    quantity: float
    price: float
    total: float
    transaction_type: str
    position_type: str  # 'long' or 'short' position type

class TransactionCreate(TransactionBase):
    user_id: int
    order_id: int

class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime
    user_id: int
    order_id: int

    class Config:
        orm_mode = True
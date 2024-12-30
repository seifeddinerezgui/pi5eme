# app/schemas/price_alert.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PriceAlertCreate(BaseModel):
    symbol: str
    price_target: float
    direction: str

class PriceAlertResponse(BaseModel):
    id: int
    symbol: str
    price_target: float
    direction: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Remplace `orm_mode` par `from_attributes`


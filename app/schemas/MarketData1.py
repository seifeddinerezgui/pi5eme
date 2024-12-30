# app/schemas.py
from pydantic import BaseModel
from datetime import datetime

class MarketDataCreate(BaseModel):
    symbol: str
    current_price: float
    high_price: float
    low_price: float
    volume: int
    last_updated: datetime

    class Config:
        orm_mode = True

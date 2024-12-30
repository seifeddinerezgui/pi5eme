from pydantic import BaseModel
from datetime import datetime

class TradeCreate(BaseModel):
    scenario_id: int
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: float
    price: float  # Price at which the trade was executed

class TradeResponse(BaseModel):
    id: int
    scenario_id: int
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime  # Timestamp of the trade

    class Config:
        orm_mode = True

# app/schemas/order.py
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class OrderCreate(BaseModel):
    symbol: str
    quantity: float
    order_type: Literal['market', 'limit']  # Market or limit order
    action: Literal['buy', 'sell']  # Buy or sell action
    price: Optional[float] = Field(None, description="Price for limit orders")  # Optional for market orders
    take_profit: Optional[float] = Field(None, description="Take Profit price")  # New Field
    stop_loss: Optional[float] = Field(None, description="Stop Loss price")  # New Field

class OrderResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    price: Optional[float]
    order_type: str
    action: str
    status: str
    executed_at: Optional[datetime]
    take_profit: Optional[float]  # New Field
    stop_loss: Optional[float]  # New Field

    class Config:
        orm_mode = True

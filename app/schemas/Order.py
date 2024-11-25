from dataclasses import Field
from datetime import datetime

from pydantic import BaseModel
from typing import Literal, Optional


class OrderCreate(BaseModel):
    symbol: str
    quantity: float
    order_position_type: Literal['long', 'short']



class SellOrderCreate(BaseModel):
    symbol: str
    quantity: float

class OrderResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    price: float | None
    order_type: str
    order_position_type: str
    executed_at: datetime | None
    status: str
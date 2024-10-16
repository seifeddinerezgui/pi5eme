from pydantic import BaseModel
from typing import Literal

class OrderCreate(BaseModel):
    symbol: str
    quantity: float
    order_position_type: Literal['long', 'short']


class SellOrderCreate(BaseModel):
    symbol: str
    quantity: float
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScheduledOrderCreate(BaseModel):
    symbol: str  # Symbole de l'actif
    quantity: float  # Quantité d'actifs
    target_price: float = None  # Prix cible (optionnel)
    execution_date: datetime = None  # Date d'exécution (optionnel)
    order_type: str  # 'buy' ou 'sell'


class ScheduledOrderResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    target_price: Optional[float]
    execution_date: Optional[datetime]
    order_type: str
    created_at: datetime

    class Config:
        orm_mode = True

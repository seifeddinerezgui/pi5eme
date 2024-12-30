from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict

class HistoricalDataBase(BaseModel):
    scenario_id: int
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class HistoricalDataResponse(HistoricalDataBase):
    id: int

    class Config:
        orm_mode = True

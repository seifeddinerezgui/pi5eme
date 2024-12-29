from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict


class HistoricalScenarioBase(BaseModel):
    name: str
    symbol: str
    start_date: date
    end_date: date
    additional_info: Optional[Dict]

class HistoricalScenarioCreate(BaseModel):
    name: str
    symbol: str
    start_date: date
    end_date: date
    additional_info: Optional[Dict] = None


class HistoricalScenarioResponse(HistoricalScenarioBase):
    id: int

    class Config:
        orm_mode = True

# app/schemas/portfolio.py
from pydantic import BaseModel

class PortfolioBase(BaseModel):
    balance: float

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioResponse(PortfolioBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
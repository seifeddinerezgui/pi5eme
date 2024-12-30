# app/schemas/asset.py
from pydantic import BaseModel

class AssetBase(BaseModel):
    symbol: str
    quantity: float
    price_bought: float
    position_type: str  # 'long' or 'short' position type

class AssetOut(BaseModel):
    id: int
    symbol: str
    quantity: float
    price_bought: float
    position_type: str
    portfolio_id: int

class AssetCreate(AssetBase):
    portfolio_id: int

class AssetResponse(AssetBase):
    id: int
    portfolio_id: int

    class Config:
        orm_mode = True
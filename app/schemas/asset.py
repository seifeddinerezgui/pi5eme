# app/schemas/asset.py
from pydantic import BaseModel

class AssetBase(BaseModel):
    symbol: str
    quantity: float
    price_bought: float

class AssetCreate(AssetBase):
    portfolio_id: int

class AssetResponse(AssetBase):
    id: int
    portfolio_id: int

    class Config:
        orm_mode = True
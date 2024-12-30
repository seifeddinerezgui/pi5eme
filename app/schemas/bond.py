from pydantic import BaseModel

class BondBase(BaseModel):
    face_value: float
    coupon_rate: float
    market_rate: float
    maturity: int
    payment_frequency: int
    

class BondCreate(BondBase):
    pass


class BondRead(BondBase):
    bond_id: int

    class Config:
        orm_mode = True
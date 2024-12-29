# Request/response validation
from pydantic import BaseModel

# User schema for requests/responses
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Portfolio schema
class PortfolioResponse(BaseModel):
    id: int
    balance: float

    class Config:
        orm_mode = True


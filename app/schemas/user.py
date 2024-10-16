from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    age: Optional[int] = None  # Age of the user
    experience: Optional[str] = None  # Experience level (optional)
    education_level: Optional[str] = None  # Level of education (optional)
    proficiency: Optional[str] = None  # Proficiency in trading (optional)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int
    experience: Optional[str]
    education_level: Optional[str]
    proficiency: Optional[str]

    class Config:
        orm_mode = True

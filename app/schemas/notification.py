from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    message: str
    created_at: datetime
    read: Optional[bool] = False
    user_id: int

    class Config:
        from_attributes = True  # Remplace `orm_mode` par `from_attributes`

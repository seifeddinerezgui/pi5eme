from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)
    price_target = Column(Float)
    direction = Column(String(4))  # 'up' or 'down'
    created_at = Column(DateTime, default=datetime.utcnow)  # Initialiser la date actuelle
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="price_alerts")

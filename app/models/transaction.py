from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)  # Asset symbol
    quantity = Column(Float)
    price = Column(Float)
    total = Column(Float)
    transaction_type = Column(String(4))  # 'buy' or 'sell'
    position_type = Column(String(5), nullable=False)  # 'long' or 'short'
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey to User

    # Relationships
    user = relationship("User", back_populates="transactions")

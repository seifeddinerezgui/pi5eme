# app/models/order.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=True)  # Price for limit orders
    order_type = Column(String(6), nullable=False)  # 'market' or 'limit'
    action = Column(String(4), nullable=False)  # 'buy' or 'sell'
    status = Column(String(10), default="pending")  # 'pending', 'executed'
    executed_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")

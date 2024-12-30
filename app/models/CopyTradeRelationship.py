# app/models/copy_trade_relationship.py
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class CopyTradeRelationship(Base):
    __tablename__ = "copy_trade_relationships"

    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    percentage_to_invest = Column(Float, default=1.0)  # Par défaut, 100% des montants du trader
    created_at = Column(DateTime, default=datetime.utcnow)

    trader = relationship("User", foreign_keys=[trader_id], back_populates="followers")
    follower = relationship("User", foreign_keys=[follower_id], back_populates="leaders")

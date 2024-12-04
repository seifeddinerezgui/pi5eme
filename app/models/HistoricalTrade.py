from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class HistoricalTrade(Base):
    __tablename__ = "historical_trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scenario_id = Column(Integer, ForeignKey("historical_scenarios.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="historical_trades")
    scenario = relationship("HistoricalScenario", back_populates="trades")

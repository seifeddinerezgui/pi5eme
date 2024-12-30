from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExpertTrade(Base):
    __tablename__ = "expert_trades"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("historical_scenarios.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    action = Column(String(4), nullable=False)  # 'buy' or 'sell'
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    scenario = relationship("HistoricalScenario", back_populates="expert_trades")

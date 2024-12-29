from sqlalchemy import Column, Integer, String, Date, JSON
from app.database import Base
from sqlalchemy.orm import relationship

class HistoricalScenario(Base):
    __tablename__ = "historical_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False)  # Scenario name (e.g., "COVID-19 Crash")
    symbol = Column(String(10), nullable=False)  # Stock symbol (e.g., "AAPL", "SPY")
    start_date = Column(Date, nullable=False)  # Scenario start date
    end_date = Column(Date, nullable=False)  # Scenario end date
    additional_info = Column(JSON, nullable=True)  # Additional info (e.g., description)


    trades = relationship("HistoricalTrade", back_populates="scenario")
    expert_trades = relationship("ExpertTrade", back_populates="scenario")
    historical_data = relationship("HistoricalData", back_populates="scenario", cascade="all, delete-orphan")



from sqlalchemy import Column, Integer, Float, String, DateTime
from app.database import Base
from datetime import datetime

class MarketData1(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)  # Symbole de l'actif (ex. AAPL, MSFT)
    current_price = Column(Float, nullable=False)  # Prix actuel de l'actif
    high_price = Column(Float, nullable=False)  # Prix le plus haut de la journée
    low_price = Column(Float, nullable=False)  # Prix le plus bas de la journée
    volume = Column(Integer, nullable=False)  # Volume des transactions
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Date de la dernière mise à jour

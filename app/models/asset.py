from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)  # Stock symbol or asset identifier
    quantity = Column(Float, nullable=False)
    price_bought = Column(Float, nullable=False)
    position_type = Column(String(5), nullable=False)  # 'long' or 'short'
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)  # ForeignKey to Portfolio

    # Relationship to portfolio
    portfolio = relationship("Portfolio", back_populates="assets")
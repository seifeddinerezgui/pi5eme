from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=100000.0)  # Virtual balance for trading
    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey to User

    # Relationship to user and assets
    user = relationship("User", back_populates="portfolio")
    assets = relationship("Asset", back_populates="portfolio")

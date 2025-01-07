from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)  # Length specified
    email = Column(String(255), unique=True, nullable=False)  # Length specified
    hashed_password = Column(String(128), nullable=False)  # Length specified
    age = Column(Integer, nullable=True)  # Age of the user
    experience = Column(String(255), nullable=True)  # Experience level (e.g., "beginner", "intermediate", "expert")
    education_level = Column(String(255), nullable=True)  # Level of education (e.g., "bachelor", "master")
    proficiency = Column(String(255), nullable=True)  # Proficiency in trading (e.g., "stocks", "forex", "crypto")

    # Relationships
    portfolio = relationship("Portfolio", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    orders = relationship("Order_market", back_populates="user")
    scheduled_orders = relationship("ScheduledOrder", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    price_alerts = relationship("PriceAlert", back_populates="user")
    user_lessons = relationship("UserLesson", back_populates="user")
    bonds = relationship("Bond", back_populates="user")
    notes = relationship("Note", back_populates="author")
    order = relationship("Order", back_populates="user")
    historical_trades = relationship("HistoricalTrade", back_populates="user")
    alerts = relationship("Alert", back_populates="user")  # Corrected relationship

    followers = relationship(
        "CopyTradeRelationship",
        foreign_keys="CopyTradeRelationship.trader_id",
        back_populates="trader",
        cascade="all, delete-orphan",  # Optional: to manage the lifecycle
    )

    leaders = relationship(
        "CopyTradeRelationship",
        foreign_keys="CopyTradeRelationship.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",  # Optional
    )

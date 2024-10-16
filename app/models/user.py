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


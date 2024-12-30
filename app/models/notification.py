from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Spécifier une longueur pour le VARCHAR

    message = Column(String(255), nullable=False)  # Spécifier une longueur pour le VARCHAR
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="notifications")

from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Note(Base):
    __tablename__="notes"
    id = Column(Integer, primary_key=True,index=True)
    content = Column(Text(65000),nullable=False)
    created_at = Column(DateTime,default=datetime.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="notes")

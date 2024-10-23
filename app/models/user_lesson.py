from sqlalchemy import Table, ForeignKey, Integer, Column, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class UserLesson(Base):
    __tablename__= "user_lesson"

    user_id = Column(Integer, ForeignKey('users.id'),primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), primary_key=True)
    seen = Column(Boolean, default=False)

    user = relationship("User",back_populates="user_lessons")
    lesson = relationship("Lesson", back_populates='user_lessons')
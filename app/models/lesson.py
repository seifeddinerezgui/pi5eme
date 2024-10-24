from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models import user_lesson


class Lesson(Base):
    __tablename__="lessons"
    id = Column(Integer, primary_key=True,index=True)
    title= Column(String(255),unique=True)
    url = Column(String(500),unique=True)
    user_lessons = relationship('UserLesson', back_populates="lesson")


from sqlalchemy import Column, Integer, Boolean, String, ARRAY
from sqlalchemy.orm import relationship

from app.database import Base
from app.models import user_lesson


class Lesson(Base):
    __tablename__="lessons"
    id = Column(Integer, primary_key=True,index=True)
    title = Column(String(255),unique=True)
    url = Column(String(500),unique=True)
    first_question = Column(String(500))
    first_question_first_choice = Column(String(500))
    first_question_second_choice = Column(String(500))
    first_question_third_choice = Column(String(500))
    first_question_fourth_choice = Column(String(500))
    first_correct_answer = Column(String(500))
    second_question = Column(String(500))
    second_question_first_choice = Column(String(500))
    second_question_second_choice = Column(String(500))
    second_question_third_choice = Column(String(500))
    second_question_fourth_choice = Column(String(500))
    second_correct_answer = Column(String(500))
    note = Column(String(500))
    user_lessons = relationship('UserLesson', back_populates="lesson")


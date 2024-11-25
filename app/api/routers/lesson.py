from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lesson, User, UserLesson

router = APIRouter()
class AddLessonRequest(BaseModel):
    title: str
    url: str
    first_question: str
    first_question_first_choice : str
    first_question_second_choice : str
    first_question_third_choice : str
    first_question_fourth_choice :str
    first_correct_answer: str
    second_question: str
    second_question_first_choice : str
    second_question_second_choice : str
    second_question_third_choice : str
    second_question_fourth_choice : str
    second_correct_answer: str
    note: str

@router.post('/')
async def add_lesson(add_request: AddLessonRequest, db: Session = Depends(get_db)):
    lesson =  Lesson(
        title= add_request.title,
        url= add_request.url,
        first_question=add_request.first_question,
        first_question_first_choice =add_request.first_question_first_choice,
        first_question_second_choice = add_request.first_question_second_choice,
        first_question_third_choice = add_request.first_question_third_choice,
        first_question_fourth_choice = add_request.first_question_fourth_choice,
        first_correct_answer= add_request.first_correct_answer,
        second_question= add_request.second_question,
        second_question_first_choice = add_request.second_question_first_choice,
        second_question_second_choice = add_request.second_question_second_choice,
        second_question_third_choice = add_request.second_question_third_choice,
        second_question_fourth_choice = add_request.second_question_fourth_choice,
        second_correct_answer=add_request.second_correct_answer,
        note=add_request.note
    )
    db.add(lesson)
    db.commit()
    users = db.query(User).all()
    for user in users:
        user_lesson = db.query(UserLesson).filter_by(user_id=user.id,lesson_id=lesson.id).first()
        if not user_lesson:
            new_user_lesson = UserLesson(user_id=user.id,lesson_id=lesson.id, seen =False)
            db.add(new_user_lesson)
    db.commit()
    db.refresh(lesson)
    return lesson




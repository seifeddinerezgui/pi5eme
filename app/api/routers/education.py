from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import get_db
from app.models import User, UserLesson

router =  APIRouter()

class LessonResponse(BaseModel):
    id: int
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
    class Config:
        orm_mode = True
class UserLessonResponse(BaseModel):
    lesson: LessonResponse
    seen: bool

    class Config:
        orm_mode = True



@router.get('/current/lessons',response_model=list[UserLessonResponse])
async def get_lessons(request : Request, db: Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    lessons = db.query(UserLesson).filter_by(user_id = id).all()
    return [
        UserLessonResponse(
            lesson=LessonResponse(id=user_lesson.lesson.id, title=user_lesson.lesson.title, url=user_lesson.lesson.url,
                                    first_question= user_lesson.lesson.first_question,
                                    first_question_first_choice = user_lesson.lesson.first_question_first_choice,
                                    first_question_second_choice= user_lesson.lesson.first_question_second_choice,
                                    first_question_third_choice = user_lesson.lesson.first_question_third_choice,
                                    first_question_fourth_choice = user_lesson.lesson.first_question_fourth_choice,
                                    first_correct_answer= user_lesson.lesson.first_correct_answer,
                                    second_question= user_lesson.lesson.second_question,
                                    second_question_first_choice = user_lesson.lesson.second_question_first_choice,
                                    second_question_second_choice = user_lesson.lesson.second_question_second_choice,
                                    second_question_third_choice = user_lesson.lesson.second_question_third_choice,
                                    second_question_fourth_choice = user_lesson.lesson.second_question_fourth_choice,
                                    second_correct_answer= user_lesson.lesson.second_correct_answer,
                                    note= user_lesson.lesson.note                   ),
            seen=user_lesson.seen
        )
        for user_lesson in lessons
    ]


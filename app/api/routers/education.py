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
            lesson=LessonResponse(id=user_lesson.lesson.id, title=user_lesson.lesson.title, url=user_lesson.lesson.url),
            seen=user_lesson.seen
        )
        for user_lesson in lessons
    ]


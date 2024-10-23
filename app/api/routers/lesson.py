from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lesson, User, UserLesson

router = APIRouter()
class AddLessonRequest(BaseModel):
    title: str
    url: str

@router.post('/')
async def add_lesson(add_request: AddLessonRequest, db: Session = Depends(get_db)):
    lesson =  Lesson(
        title= add_request.title,
        url= add_request.url
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




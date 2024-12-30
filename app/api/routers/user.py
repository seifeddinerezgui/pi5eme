from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.database import get_db
from app.models import User

router = APIRouter()


class Profile(BaseModel):
    username: str
    email: str
    experience: str
    proficiency: str

@router.get('/current')
async def get_current_user(request : Request, db: Session = Depends(get_db)):
    current = db.query(User).filter(User.username == request.state.user).first()
    if not current: raise HTTPException(status_code=400,detail="user not found")
    return {
        "username" : current.username,
        "email" : current.email,
        "experience" : current.experience,
        "proficiency" : current.proficiency
    }

# Route pour récupérer la liste des utilisateurs
@router.get("/users", response_model=list[dict])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "age": user.age if user.age else None,
            "experience": user.experience if user.experience else None,
            "education_level": user.education_level if user.education_level else None
        }
        for user in users
    ]



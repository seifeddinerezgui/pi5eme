from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import get_db
from app.models import User
from app.models.note import Note

router = APIRouter()

class addNoteRequest(BaseModel):
    content: str

@router.post("/")
async def add_note(request : Request, add_request : addNoteRequest, db : Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    note = Note(content = add_request.content,user_id = id)
    db.add(note)
    db.commit()
    return note

@router.get("/current/all")
async def get_all_notes(request : Request, db : Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    notes = db.query(Note).filter(Note.user_id == id).all()
    return notes


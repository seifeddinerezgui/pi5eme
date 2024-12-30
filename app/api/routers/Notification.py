from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notification import NotificationResponse
from app.services.NotificationService import create_notification, get_notifications, mark_notification_as_read
from app.models.user import User  # Assure-toi d'importer le modèle User

router = APIRouter()

# Fonction pour récupérer l'utilisateur statique (id=1)
def get_static_user(db: Session):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=list[NotificationResponse])
def read_notifications(db: Session = Depends(get_db)):
    user = get_static_user(db)  # Utilisateur statique
    return get_notifications(db=db, user_id=user.id)

@router.post("/", response_model=NotificationResponse)
def add_notification(message: str,title: str, db: Session = Depends(get_db)):
    user = get_static_user(db)  # Utilisateur statique
    return create_notification(db=db, title=title,message=message, user_id=user.id)

@router.patch("/{notification_id}", response_model=dict)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    user = get_static_user(db)  # Utilisateur statique
    success = mark_notification_as_read(db=db, notification_id=notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"detail": "Notification marked as read"}

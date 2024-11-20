# app/services/notification_service.py

from sqlalchemy.orm import Session
from app.models import Notification
from app.schemas.notification import NotificationResponse

def create_notification(db: Session, title: str,message: str, user_id: int) -> NotificationResponse:
    new_notification = Notification(
        title=title,
        message=message,
        user_id=user_id
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return NotificationResponse.from_orm(new_notification)

def get_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(db: Session, notification_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.read = True
        db.commit()
        return True
    return False

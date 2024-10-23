from sqlalchemy.orm import Session
from app.models import PriceAlert
from app.schemas.price_alert import PriceAlertCreate, PriceAlertResponse
from datetime import datetime  # Ajoute cette ligne pour importer datetime

def create_price_alert(db: Session, alert: PriceAlertCreate, user_id: int) -> PriceAlertResponse:
    new_alert = PriceAlert(
        symbol=alert.symbol,
        price_target=alert.price_target,
        direction=alert.direction,
        user_id=user_id,
        created_at=datetime.utcnow()  # Assure-toi que ce champ est bien initialisé
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return PriceAlertResponse.from_orm(new_alert)



def get_price_alerts(db: Session, user_id: int):
    return db.query(PriceAlert).filter(PriceAlert.user_id == user_id).all()

def delete_price_alert(db: Session, alert_id: int):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if alert:
        db.delete(alert)
        db.commit()
        return True
    return False

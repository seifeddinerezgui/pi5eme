from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.price_alert import PriceAlertCreate, PriceAlertResponse
from app.services.PriceAlertSerice import create_price_alert, get_price_alerts, delete_price_alert

router = APIRouter()

# Utilisateur statique avec l'ID 1
STATIC_USER_ID = 1

@router.post("/", response_model=PriceAlertResponse)
def add_price_alert(alert: PriceAlertCreate, db: Session = Depends(get_db)):
    """
    Ajoute une nouvelle alerte de prix pour l'utilisateur avec ID 1.
    """
    return create_price_alert(db=db, alert=alert, user_id=STATIC_USER_ID)

@router.get("/", response_model=list[PriceAlertResponse])
def read_price_alerts(db: Session = Depends(get_db)):
    """
    Récupère toutes les alertes de prix pour l'utilisateur avec ID 1.
    """
    return get_price_alerts(db=db, user_id=STATIC_USER_ID)

@router.delete("/{alert_id}", response_model=dict)
def remove_price_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Supprime une alerte de prix pour l'utilisateur avec ID 1.
    """
    success = delete_price_alert(db=db, alert_id=alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Price alert not found")
    return {"detail": "Price alert deleted successfully"}

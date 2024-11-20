from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import PriceAlert
from app.schemas.price_alert import PriceAlertCreate, PriceAlertResponse
from datetime import datetime  # Ajoute cette ligne pour importer datetime
from app.models import notification
from app.services.price_fetch import getData  # Import de la méthode getData
from app.services.NotificationService import create_notification
from app.services.MarketDataService import MarketDataService  # Import de MarketDataService


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

# Fonction qui vérifie les alertes de prix toutes les minutes
def check_price_alerts():
    db = SessionLocal()
    try:
        # Récupérer toutes les alertes de prix
        alerts = db.query(PriceAlert).all()

        for alert in alerts:
            # Récupérer le prix actuel via la méthode get_market_data
            current_price = MarketDataService.get_market_data(alert.symbol)

            if current_price:
                print(f"Current price for {alert.symbol}: {current_price}")
                
                # Comparer le prix actuel avec le seuil de l'alerte
                if alert.direction == "up" and current_price >= alert.price_target:
                    create_notification(db, f"Price alert: {alert.symbol} has reached {current_price}", alert.user_id)
                elif alert.direction == "down" and current_price <= alert.price_target:
                    create_notification(db, f"Price alert: {alert.symbol} has dropped to {current_price}", alert.user_id)
                else:
                    
                    pass
        db.commit()
    finally:
        db.close()



# Configuration du scheduler APScheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_price_alerts, 'interval', minutes=8)  # Exécuter toutes les minutes
    scheduler.start()

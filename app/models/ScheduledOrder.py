from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ScheduledOrder(Base):
    __tablename__ = "scheduled_orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)  # Symbole de l'actif (ex. AAPL)
    quantity = Column(Float, nullable=False)  # Quantité d'actifs
    target_price = Column(Float, nullable=True)  # Prix cible pour l'exécution de l'ordre
    execution_date = Column(DateTime, nullable=True)  # Date planifiée pour exécuter l'ordre
    order_type = Column(String(4), nullable=False)  # 'buy' ou 'sell'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Date de création

    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey vers l'utilisateur
    user = relationship("User", back_populates="scheduled_orders")  # Relation avec l'utilisateur

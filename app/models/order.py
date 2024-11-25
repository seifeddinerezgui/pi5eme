# app/models/order.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)  # Symbole de l'actif (ex. AAPL)
    quantity = Column(Float, nullable=False)  # Quantité d'actifs
    price = Column(Float, nullable=True)  # Prix limite pour l'ordre, peut être None pour un ordre au marché
    order_type = Column(String(8), nullable=False)  # 'buy' ou 'sell'
    action = Column(String(6), nullable=False) # 'market' or 'limit'
    order_position_type = Column(String(5), nullable=False)  # 'long' ou 'short'
    executed_at = Column(DateTime, nullable=True)  # Date d'exécution pour les ordres instantanés
    status =Column(String(10), nullable=True)


    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey vers l'utilisateur
    user = relationship("User", back_populates="orders")  # Relation avec l'utilisateur

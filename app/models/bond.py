from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Float, ForeignKey, Integer

class Bond(Base):
     __tablename__ = "Bond"
     
     bond_id= Column(Integer, primary_key=True, index=True)
     face_value= Column(Float) # Valeur nominale (F)
     coupon_rate= Column(Float) # Taux de coupon (par exemple 5% -> 0.05)
     market_rate= Column(Float)  # Taux du marché (r)
     maturity= Column(Integer)  # Durée jusqu'à l'échéance en années (N)
     payment_frequency= Column(Integer)  # Fréquence des paiements (1 = annuel, 2 = semestriel, etc.)
    
     user_id = Column(Integer, ForeignKey('users.id'))
     user = relationship("User", back_populates="bonds")

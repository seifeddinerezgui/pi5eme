# app/services/copy_trade_service.py
from app.models.order_market import Order_market
from app.models.user import User
from app.models.CopyTradeRelationship import CopyTradeRelationship
from sqlalchemy.orm import Session 
from datetime import datetime

def execute_copy_trade(order: Order_market, db: Session):
    """
    Crée un nouvel ordre pour un trader et copie cet ordre pour tous ses copieurs.
    """
    # Ajoutez l'ordre du trader à la base de données
    db.add(order)
    db.commit()  # Engagez les modifications pour récupérer l'ID de l'ordre du trader

    # Récupérez les copieurs liés à ce trader
    relationships = db.query(CopyTradeRelationship).filter(CopyTradeRelationship.trader_id == order.user_id).all()

    for relationship in relationships:
        follower_id = relationship.follower_id
        percentage = relationship.percentage_to_invest

        # Calculez la quantité copiée
        copied_quantity = order.quantity * percentage

        # Vérifiez le solde du copieur
        follower = db.query(User).filter(User.id == follower_id).first()
        total_cost = order.price * copied_quantity if order.price else 0
        if order.order_type == "buy" and follower.balance < total_cost:
            # Skip if insufficient balance
            continue

        # Créez un nouvel ordre pour le copieur
        copied_order = Order_market(
            symbol=order.symbol,
            quantity=copied_quantity,
            price=order.price,
            order_type=order.order_type,
            order_position_type=order.order_position_type,
            executed_at=order.executed_at,
            user_id=follower_id  # Assigné au copieur
        )
        db.add(copied_order)

        # Mettez à jour le solde du copieur si c'est un achat
        if order.order_type == "buy":
            follower.balance -= total_cost

    db.commit()  # Engagez toutes les modifications
####################################################################################################
def copy_order_for_followers(order: Order_market, db: Session):
    """
    Copie un ordre du trader à tous les copieurs qui le suivent.
    """
    # Rechercher les followers actifs de ce trader
    relationships = db.query(CopyTradeRelationship).filter_by(trader_id=order.user_id).all()

    if not relationships:
        return  # Aucun follower trouvé pour ce trader

    for relationship in relationships:
        # Calculez la quantité basée sur le pourcentage défini
        copied_quantity = order.quantity * relationship.percentage_to_invest

        # Créez un nouvel ordre pour chaque follower
        copied_order = Order_market(
            symbol=order.symbol,
            quantity=copied_quantity,
            price=order.price,
            order_type=order.order_type,
            order_position_type=order.order_position_type,
            executed_at=None,  # Pas encore exécuté
            user_id=relationship.follower_id
        )
        db.add(copied_order)

    db.commit()

# app/api/copy_trade.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.CopyTradeRelationship import CopyTradeRelationship
from app.models.order_market import Order_market
from app.models.user import User
from app.services.copy_trade_service import execute_copy_trade
from app.schemas.copy_trade import  MessageResponse
from typing import List
from starlette.requests import Request

router = APIRouter()

@router.post("/follow/{trader_id}", response_model=MessageResponse)
def follow_trader(trader_id: int, request : Request, percentage_to_invest:int , db: Session = Depends(get_db)):
    """
    Permet à un utilisateur de suivre un trader pour le copy trade.
    """
    id = db.query(User).filter(User.username == request.state.user).first().id
    # Vérifiez si la relation existe déjà
    existing_relationship = db.query(CopyTradeRelationship).filter_by(
        trader_id=trader_id, 
        follower_id=id
    ).first()
    if existing_relationship:
        raise HTTPException(status_code=400, detail="Vous suivez déjà ce trader.")

    # Créez une nouvelle relation de copy trade
    relationship = CopyTradeRelationship(
        trader_id=trader_id,
        follower_id=id,
        percentage_to_invest=percentage_to_invest
    )
    db.add(relationship)
    db.commit()

    return {"message": "Vous suivez désormais ce trader."}


@router.delete("/unfollow/{trader_id}", response_model=MessageResponse)
def unfollow_trader(
    trader_id: int, 
    follower_id: int, 
    db: Session = Depends(get_db)
):
    """
    Permet à un utilisateur de ne plus suivre un trader.
    """
    relationship = db.query(CopyTradeRelationship).filter_by(
        trader_id=trader_id, 
        follower_id=follower_id
    ).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Relation non trouvée.")

    db.delete(relationship)
    db.commit()

    return {"message": "Vous ne suivez plus ce trader."}


@router.post("/execute/{order_id}", response_model=MessageResponse)
def execute_order(
    order_id: int, 
    db: Session = Depends(get_db)
):
    """
    Exécute le copy trade pour un ordre spécifique.
    """
    # Récupérer l'ordre à exécuter
    order = db.query(Order_market).filter(Order_market.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ordre non trouvé.")

    # Exécuter le copy trade
    try:
        execute_copy_trade(order, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Copy trade exécuté avec succès."}

@router.get("/users", response_model=List[dict])
def get_users_with_orders(db: Session = Depends(get_db)):
    """
    Récupère tous les utilisateurs avec leurs ordres et leurs balances.
    """
    users = db.query(User).all()
    result = []
    for user in users:
        orders = db.query(Order_market).filter(Order_market.user_id == user.id).all()
        user_data = {
            "id": user.id,
            "name": user.name,
            "balance": user.balance,
            "orders": [{"id": order.id, "symbol": order.symbol, "amount": order.amount} for order in orders]
        }
        result.append(user_data)
    return result

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.Order import OrderCreate, SellOrderCreate, OrderResponse
from app.services.OrderService import OrderService
from starlette.requests import Request
from typing import List
from app.database import get_db
from app.models import User, Order

router = APIRouter()
@router.post("/buy", response_model=OrderCreate)
def create_buy_order(request : Request, order: OrderCreate, db: Session = Depends(get_db)):
    # Call the OrderService to create the buy order
    id = db.query(User).filter(User.username == request.state.user).first().id
    return OrderService.create_buy_order(id, order.symbol, order.quantity, order.order_position_type, db)


@router.post("/sell", response_model=OrderCreate)
def create_sell_order(request : Request, order: SellOrderCreate, db: Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    """Endpoint to create a sell order for a user."""
    return OrderService.create_sell_order(id, order.symbol, order.quantity, db)


@router.get("/all", response_model=List[OrderResponse])
def get_user_orders(request: Request, db: Session = Depends(get_db)):
    """
    Récupérer tous les ordres de l'utilisateur connecté.
    """
    # Récupération de l'utilisateur connecté via le request.state.user
    user = db.query(User).filter(User.username == request.state.user).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    orders = db.query(Order).filter(Order.user_id == user.id).all()

    if not orders:
        raise HTTPException(status_code=404, detail="Aucun ordre trouvé pour cet utilisateur")

    return orders
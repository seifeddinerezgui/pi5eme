from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.Order import OrderCreate, SellOrderCreate
from app.services.OrderService import OrderService


router = APIRouter()
@router.post("/{user_id}/buy", response_model=OrderCreate)
def create_buy_order(user_id: int, order: OrderCreate, db: Session = Depends(get_db)):
    # Call the OrderService to create the buy order
    return OrderService.create_buy_order(user_id, order.symbol, order.quantity, order.order_position_type, db)


@router.post("/{user_id}/sell", response_model=OrderCreate)
def create_sell_order(user_id: int, order: SellOrderCreate, db: Session = Depends(get_db)):
    """Endpoint to create a sell order for a user."""
    return OrderService.create_sell_order(user_id, order.symbol, order.quantity, db)

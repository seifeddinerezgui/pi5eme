from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.schemas.Order import OrderCreate, OrderResponse
from app.services.OrderService import OrderService
from app.api.routers.auth import get_current_user


router = APIRouter()

@router.post("/", response_model=OrderResponse)
def place_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Call the OrderService to place the order
    return OrderService.create_order(
        user_id=user.id,
        symbol=order.symbol,
        quantity=order.quantity,
        order_type=order.order_type,
        action=order.action,
        price=order.price,
        db=db
    )

@router.get("/", response_model=list[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Fetch and return user orders
    return db.query(Order).filter(Order.user_id == user.id).all()

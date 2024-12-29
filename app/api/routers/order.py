from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, User
from app.schemas.Order import OrderCreate, OrderResponse
from app.services.OrderService import OrderService
from app.api.routers.auth import get_current_user
from starlette.requests import Request



router = APIRouter()

@router.post("/", response_model=OrderResponse)
def place_order(
    request: Request,
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    user_id = db.query(User).filter(User.username == request.state.user).first().id
    return OrderService.create_order(
        user_id=user_id,
        symbol=order.symbol,
        quantity=order.quantity,
        order_type=order.order_type,
        action=order.action,
        price=order.price,
        take_profit=order.take_profit,  # Pass TP
        stop_loss=order.stop_loss,  # Pass SL
        db=db
    )


@router.get("/", response_model=list[OrderResponse])
def get_user_orders(
    request:Request,
    db: Session = Depends(get_db),
):
    id = db.query(User).filter(User.username == request.state.user).first().id
    # Fetch and return user orders
    return db.query(Order).filter(Order.user_id == id).all()

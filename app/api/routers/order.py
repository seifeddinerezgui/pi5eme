from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
<<<<<<< HEAD
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
=======
from app.models import Order, User
from app.schemas.Order import OrderCreate, OrderResponse
from app.services.OrderService import OrderService
from app.api.routers.auth import get_current_user
from starlette.requests import Request



router = APIRouter()

@router.post("/", response_model=OrderResponse)
def place_order(
    request:Request,
    order: OrderCreate,
    db: Session = Depends(get_db)  
):
    id = db.query(User).filter(User.username == request.state.user).first().id
    # Call the OrderService to place the order
    return OrderService.create_order(
        user_id=id,
        symbol=order.symbol,
        quantity=order.quantity,
        order_type=order.order_type,
        action=order.action,
        price=order.price,
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
>>>>>>> fce8bc65103dd6ef43246bdd00c796ddd723d4cd

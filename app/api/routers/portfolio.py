# app/api/routers/portfolio.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.routers.auth import get_current_user
from app.models import Portfolio, User

router = APIRouter()

@router.get("/balance")
def get_portfolio_balance(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Query the user's portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Return the balance
    return {"balance": portfolio.balance}

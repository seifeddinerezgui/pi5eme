# app/api/routers/portfolio.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import get_db
from app.models import Portfolio, User

router = APIRouter()

@router.get("/balance")
def get_portfolio_balance(request : Request, db: Session = Depends(get_db)):
    # Query the user's portfolio
    id = db.query(User).filter(User.username == request.state.user).first().id
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Return the balance
    return {"balance": portfolio.balance}

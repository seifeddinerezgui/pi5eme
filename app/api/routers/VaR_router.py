# var_router.py

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.services.VarCalculatorService import VarCalculatorService
from app.database import get_db
from app.models import Portfolio, User

router = APIRouter()

@router.get("/var/{symbol}")
async def get_var(symbol: str, request: Request, db: Session = Depends(get_db), confidence_level: float = 0.95):
    """
    Endpoint to calculate Value-at-Risk (VaR) for a given symbol with user's portfolio value.

    Parameters:
    - symbol: The stock ticker symbol.
    - confidence_level: Confidence level for VaR calculation, default is 0.95 (95%).

    Returns:
    - VaR value for the specified symbol, confidence level, and portfolio balance.
    """
    try:
        # Retrieve the current user's portfolio balance
        user = db.query(User).filter(User.username == request.state.user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        portfolio_balance = portfolio.balance

        # Calculate VaR using portfolio balance
        var_value = VarCalculatorService.calculate_var(symbol, portfolio_balance, confidence_level)
        return {"symbol": symbol, "confidence_level": confidence_level, "VaR": var_value, "portfolio_balance": portfolio_balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

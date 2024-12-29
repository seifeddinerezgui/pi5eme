# app/api/routers/portfolio.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.database import get_db
from app.models import Portfolio, User,Order

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
@router.get("/percentages")
def get_asset_percentages(request: Request, db: Session = Depends(get_db)):
    # Récupérer l'utilisateur à partir de la requête
    user = db.query(User).filter(User.username == request.state.user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupérer le portefeuille de l'utilisateur
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Calculer les pourcentages des actifs
    from app.services.portfolio_management import calculate_asset_percentages
    try:
        asset_percentages = calculate_asset_percentages(portfolio.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while calculating percentages")

    # Retourner les pourcentages
    return {"asset_percentages": asset_percentages}

@router.get("/all-ranks")
def get_all_user_ranks(db: Session = Depends(get_db)):
    from app.services.portfolio_management import get_all_user_ranks_by_balance

    # Calculer les rangs de tous les utilisateurs
    user_ranks = get_all_user_ranks_by_balance(db)

    # Vérifier s'il y a des utilisateurs
    if not user_ranks:
        raise HTTPException(status_code=404, detail="No users found")

    # Retourner les rangs
    return {"user_ranks": user_ranks}
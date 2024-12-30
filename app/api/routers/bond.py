from typing import List
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.models.user import User
from app.schemas.bond import BondCreate
from app.schemas.bond import BondRead
import app
from app.models.bond import Bond
from app.models.portfolio import Portfolio
from app.services.bond import add_bond, calculate_bond_price, calculate_zero_coupon_bonds_for_coverage, portfolio_risk_analysis, simulate_portfolio_with_bond, suggested_bonds_for_coverage

router = APIRouter()

#cv
@router.post("/bonds/", response_model=BondCreate)
def create_bond(request : Request,bond: BondCreate, db: Session = Depends(get_db)):
    try:
        id = db.query(User).filter(User.username == request.state.user).first().id
        return add_bond( id,db, bond)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating bond: {e}")

# cv
@router.post("/calculate_bond")
def calculate_bond(request : Request, db: Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    result = calculate_bond_price(db,id)
    return {
        "price": result["price"],
        "modified_duration": result["modified_duration"],
        "coupon": result["coupon"],
        "periode": result["periode"]
    }

#cv
@router.post("/portfolio/buy_bond/{bond_id}")
def buy_bond_for_portfolio(request : Request, bond_id: int, db: Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    return simulate_portfolio_with_bond(db, id, bond_id)
####################################################
#a voir
@router.post("/portfolio/risk_analysis")
def risk_analysis(request : Request, db: Session = Depends(get_db)):
    id = db.query(User).filter(User.username == request.state.user).first().id
    return portfolio_risk_analysis(db,id)

#a voir
@router.post("/portfolio/zero_coupon_coverage")
def zero_coupon_coverage(request : Request, db: Session = Depends(get_db)):
    user_id = db.query(User).filter(User.username == request.state.user).first().id
    return calculate_zero_coupon_bonds_for_coverage(db, user_id)

#a voir
@router.get("/portfolio/suggested_bonds")
def suggested_bonds(request : Request, db: Session = Depends(get_db)):
    user_id = db.query(User).filter(User.username == request.state.user).first().id
    return suggested_bonds_for_coverage(db, user_id)

#cv
@router.get("/bonds/", response_model=List[BondRead])
def get_all_bonds(request : Request,db: Session = Depends(get_db)):
    bonds = db.query(models.Bond).all()
    return bonds

#cv
@router.get("/user/bonds")
def get_user_bonds(request : Request, db: Session = Depends(get_db)):
    user_id = db.query(User).filter(User.username == request.state.user).first().id
    bonds = db.query(models.Bond).filter(models.Bond.user_id == user_id).all()
    return bonds
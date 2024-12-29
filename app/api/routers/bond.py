from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.schemas.bond import BondCreate
from app.schemas.bond import BondRead
import app
from app.models.bond import Bond
from app.models.portfolio import Portfolio
from app.services.bond import add_bond, calculate_bond_price, calculate_zero_coupon_bonds_for_coverage, portfolio_risk_analysis, simulate_portfolio_with_bond, suggested_bonds_for_coverage

router = APIRouter()

#cv
@router.post("/bonds/", response_model=BondCreate)
def create_bond(bond: BondCreate, db: Session = Depends(get_db)):
    try:
        return add_bond(db, bond)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating bond: {e}")

# cv
@router.post("/calculate_bond/{id}")
def calculate_bond(id: int, db: Session = Depends(get_db)):
    result = calculate_bond_price(db,id)
    return {
        "price": result["price"],
        "modified_duration": result["modified_duration"],
        "coupon": result["coupon"],
        "periode": result["periode"]
    }

#cv
@router.post("/portfolio/{user_id}/buy_bond/{bond_id}")
def buy_bond_for_portfolio(user_id: int, bond_id: int, db: Session = Depends(get_db)):
    return simulate_portfolio_with_bond(db, user_id, bond_id)

#a voir
@router.post("/portfolio/{user_id}/risk_analysis")
def risk_analysis(user_id: int, db: Session = Depends(get_db)):
    return portfolio_risk_analysis(db, user_id)

#a voir
@router.post("/portfolio/{user_id}/zero_coupon_coverage")
def zero_coupon_coverage(user_id: int, db: Session = Depends(get_db)):
    return calculate_zero_coupon_bonds_for_coverage(db, user_id)

#a voir
@router.get("/portfolio/{user_id}/suggested_bonds")
def suggested_bonds(user_id: int, db: Session = Depends(get_db)):
    return suggested_bonds_for_coverage(db, user_id)

#cv
@router.get("/bonds/", response_model=List[BondRead])
def get_all_bonds(db: Session = Depends(get_db)):
    bonds = db.query(models.Bond).all()
    return bonds

#cv
@router.get("/user/{user_id}/bonds")
def get_user_bonds(user_id: int, db: Session = Depends(get_db)):
    bonds = db.query(models.Bond).filter(models.Bond.user_id == user_id).all()
    return bonds






from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Asset  # Import your Asset model
from app.schemas.asset import AssetOut

router = APIRouter()

# Display method to get all assets
@router.get("/all", response_model=List[AssetOut])
def get_assets(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found")
    return assets

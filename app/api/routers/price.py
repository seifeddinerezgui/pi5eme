from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse

from app.PriceRecommender import PriceRecommender

router = APIRouter()

@router.get("/recommendation/{symbol}")
async def get_recommendation(symbol: str):
    try:
        recommender = PriceRecommender(symbol)
        recommendation = recommender.calculate_recommendation()
        return recommendation
    except Exception as e:
        return {"error": str(e)}, 500


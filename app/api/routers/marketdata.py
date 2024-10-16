# marketdata.py

from fastapi import HTTPException, APIRouter

from app.services.MarketDataService import MarketDataService

router = APIRouter()


@router.get("/data/{symbol}", response_model=dict)
async def get_market_data(symbol: str):
    """Endpoint to get market data for a given symbol."""
    try:
        price = MarketDataService.get_market_data(symbol)
        return {"symbol": symbol, "current_price": price}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
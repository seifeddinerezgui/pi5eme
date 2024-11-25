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


@router.get("/stock/{symbol}")
def get_stock_data1(symbol: str, interval: str = "1d"):
    """
    Get stock data for the given symbol and interval.
    """
    try:
        stock_data = MarketDataService.get_market_data1(symbol, interval)
        return {"data": stock_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
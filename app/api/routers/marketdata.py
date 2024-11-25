# marketdata.py

from fastapi import HTTPException, APIRouter
<<<<<<< HEAD

=======
import requests
>>>>>>> fce8bc65103dd6ef43246bdd00c796ddd723d4cd
from app.services.MarketDataService import MarketDataService

router = APIRouter()

<<<<<<< HEAD
=======
FMP_API_KEY = "a7dKVTQUqHWZVm51wvaRqJTrw6H4Hcvi"
>>>>>>> fce8bc65103dd6ef43246bdd00c796ddd723d4cd

@router.get("/data/{symbol}", response_model=dict)
async def get_market_data(symbol: str):
    """Endpoint to get market data for a given symbol."""
    try:
        price = MarketDataService.get_market_data(symbol)
        return {"symbol": symbol, "current_price": price}
    except HTTPException as e:
<<<<<<< HEAD
        raise HTTPException(status_code=e.status_code, detail=e.detail)
=======
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/intraday/{symbol}")
def get_intraday_data(symbol: str, timeframe: str = "5min", from_date: str = None, to_date: str = None):
    # Construct the API endpoint URL
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{timeframe}/{symbol}?apikey={FMP_API_KEY}"

    # Add 'from' and 'to' date filtering if provided
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"

    # Make the API request
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching intraday data")

    data = response.json()
    if not data:
        raise HTTPException(status_code=404, detail="No intraday data available")

    return data

@router.get("/historical/{symbol}")
def get_historical_data(symbol: str):
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={FMP_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data")

    data = response.json().get('historical', [])
    return data  # Return historical data as JSON
>>>>>>> fce8bc65103dd6ef43246bdd00c796ddd723d4cd

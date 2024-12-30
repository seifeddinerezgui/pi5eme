from datetime import datetime
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import ExpertTrade

FMP_API_KEY = "a7dKVTQUqHWZVm51wvaRqJTrw6H4Hcvi"

def fetch_and_cache_expert_trades(symbol: str, start_date: str, end_date: str, scenario_id: int, db: Session):
    # Step 1: Check the database for cached trades
    cached_trades = db.query(ExpertTrade).filter(ExpertTrade.scenario_id == scenario_id).all()
    if cached_trades:
        return cached_trades

    # Step 2: Fetch data from the API
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/1hour/{symbol}?apikey={FMP_API_KEY}&from={start_date}&to={end_date}"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching expert trades")

    api_trades = response.json()
    if not api_trades:
        raise HTTPException(status_code=404, detail="No expert trades available")

    # Step 3: Process and cache the API data
    expert_trades = []
    for trade in api_trades:
        expert_trade = ExpertTrade(
            scenario_id=scenario_id,
            symbol=symbol,
            action="buy" if trade["close"] > trade["open"] else "sell",  # Example logic
            price=trade["close"],
            timestamp=datetime.strptime(trade["date"], "%Y-%m-%d %H:%M:%S")
        )
        db.add(expert_trade)
        expert_trades.append(expert_trade)

    # Commit the new trades to the database
    db.commit()

    return expert_trades

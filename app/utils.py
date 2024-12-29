# app/utils.py
import bcrypt
from datetime import datetime, timedelta
from jose import jwt 
from datetime import datetime, timedelta, timezone

from app.config import settings
from datetime import datetime
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import ExpertTrade, HistoricalData, HistoricalScenario


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return the hashed password as a string
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Check if the hashed password matches the plain password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(username: str, expires_delta: timedelta):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    print(f"Token will expire at: {expire}")  # Debug: Print expiration time
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(username: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

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

def analyze_trade_performance(user_trades, expert_trades):
    """
    Analyze user trades against expert trades and calculate performance metrics.
    """
    total_trades = len(user_trades)
    winning_trades = 0
    total_profit_loss = 0.0
    expert_recommendation_matches = 0
    timing_efficiency = 0

    for trade in user_trades:
        # Check if the user trade matches an expert recommendation
        matching_expert_trade = next(
            (et for et in expert_trades if et.symbol == trade.symbol and et.action == trade.action),
            None
        )
        if matching_expert_trade:
            expert_recommendation_matches += 1

        # Calculate profit/loss
        if trade.action == "buy":
            profit_loss = (trade.price - matching_expert_trade.price) * trade.quantity if matching_expert_trade else 0
        elif trade.action == "sell":
            profit_loss = (matching_expert_trade.price - trade.price) * trade.quantity if matching_expert_trade else 0
        else:
            profit_loss = 0

        total_profit_loss += profit_loss

        # Check if trade was profitable
        if profit_loss > 0:
            winning_trades += 1

        # Timing efficiency (closer timestamp to expert trade)
        if matching_expert_trade:
            time_difference = abs((trade.timestamp - matching_expert_trade.timestamp).total_seconds())
            timing_efficiency += max(0, 1 - (time_difference / (24 * 3600)))  # Score based on proximity (normalized)

    win_ratio = winning_trades / total_trades if total_trades > 0 else 0
    recommendation_match_ratio = expert_recommendation_matches / total_trades if total_trades > 0 else 0
    average_timing_efficiency = timing_efficiency / total_trades if total_trades > 0 else 0

    # Build performance summary
    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "win_ratio": round(win_ratio * 100, 2),
        "total_profit_loss": round(total_profit_loss, 2),
        "recommendation_match_ratio": round(recommendation_match_ratio * 100, 2),
        "average_timing_efficiency": round(average_timing_efficiency * 100, 2),
    }

def fetch_and_cache_historical_data(scenario_id: int, db: Session, timeframe: str = "5min"):
    """Fetch and cache historical data for a scenario."""
    scenario = db.query(HistoricalScenario).filter(HistoricalScenario.id == scenario_id).first()
    if not scenario:
        raise ValueError("Scenario not found")

    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{timeframe}/{scenario.symbol}?apikey={FMP_API_KEY}&from={scenario.start_date}&to={scenario.end_date}"
    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError("Error fetching intraday data")

    historical_data = response.json()
    if not historical_data:
        raise ValueError("No intraday data available")

    # Store the fetched data in the database
    for entry in historical_data:
        historical_entry = HistoricalData(
            scenario_id=scenario.id,
            timestamp=entry["date"],
            open=entry["open"],
            high=entry["high"],
            low=entry["low"],
            close=entry["close"],
            volume=entry["volume"],
        )
        db.add(historical_entry)

    db.commit()
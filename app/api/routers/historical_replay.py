from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import HistoricalScenario, HistoricalTrade, User, HistoricalData
from app.schemas.HistoricalTrade import TradeCreate, TradeResponse
from app.schemas.historical_scenario import HistoricalScenarioResponse, HistoricalScenarioCreate
import requests
import time
from datetime import datetime
from app.utils import fetch_and_cache_expert_trades, analyze_trade_performance, fetch_and_cache_historical_data



FMP_API_KEY = "a7dKVTQUqHWZVm51wvaRqJTrw6H4Hcvi"

router = APIRouter()

@router.get("/scenarios", response_model=list[HistoricalScenarioResponse])
def get_scenarios(db: Session = Depends(get_db)):
    """Fetch all historical scenarios."""
    scenarios = db.query(HistoricalScenario).all()
    return scenarios


@router.get("/data/{scenario_id}")
def get_cached_historical_data(
    scenario_id: int, db: Session = Depends(get_db)
):
    """Retrieve cached historical intraday data for a scenario."""
    data = db.query(HistoricalData).filter(HistoricalData.scenario_id == scenario_id).order_by(HistoricalData.timestamp).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="No historical data found for this scenario")

    return [{"timestamp": d.timestamp, "open": d.open, "high": d.high, "low": d.low, "close": d.close, "volume": d.volume} for d in data]


@router.post("/trades", response_model=TradeResponse)
def record_trade(trade: TradeCreate, request: Request, db: Session = Depends(get_db)):
    """Record a trade for the currently connected user with the current timestamp."""
    user_id = db.query(User).filter(User.username == request.state.user).first().id

    new_trade = HistoricalTrade(
        user_id=user_id,  # Use the connected user's ID
        scenario_id=trade.scenario_id,
        symbol=trade.symbol,
        action=trade.action,
        quantity=trade.quantity,
        price=trade.price,
        timestamp=datetime.utcnow(),  # Set current time
    )
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)  # Refresh to return the created object with the ID
    return new_trade

@router.get("/analysis/{scenario_id}")
def analyze_trades(scenario_id: int, request: Request, db: Session = Depends(get_db)):
    """Analyze trades for the connected user."""
    user_id = db.query(User).filter(User.username == request.state.user).first().id

    # Fetch user trades
    user_trades = db.query(HistoricalTrade).filter(
        HistoricalTrade.scenario_id == scenario_id,
        HistoricalTrade.user_id == user_id
    ).all()

    if not user_trades:
        raise HTTPException(status_code=404, detail="No trades found for this scenario")

    # Fetch scenario details
    scenario = db.query(HistoricalScenario).filter(HistoricalScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Fetch expert trades using the hybrid approach
    expert_trades = fetch_and_cache_expert_trades(
        symbol=scenario.symbol,
        start_date=scenario.start_date,
        end_date=scenario.end_date,
        scenario_id=scenario_id,
        db=db
    )

    # Perform trade analysis
    performance_metrics = analyze_trade_performance(user_trades, expert_trades)

    return {
        "user_trades": user_trades,
        "expert_trades": expert_trades,
        "performance": performance_metrics
    }

@router.get("/trades", response_model=list[TradeResponse])
def get_user_trades(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve all trades placed by the currently connected user in historical replay mode.
    """
    # Identify the user from the request state
    user = db.query(User).filter(User.username == request.state.user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch trades made by the user
    user_trades = db.query(HistoricalTrade).filter(HistoricalTrade.user_id == user.id).all()

    if not user_trades:
        raise HTTPException(status_code=404, detail="No trades found for the user in historical replay mode.")

    return user_trades

@router.post("/scenarios")
def create_scenario(scenario: HistoricalScenarioCreate, db: Session = Depends(get_db)):
    """Create a new historical scenario and cache its data."""
    new_scenario = HistoricalScenario(
        name=scenario.name,
        symbol=scenario.symbol,
        start_date=scenario.start_date,
        end_date=scenario.end_date,
        additional_info=scenario.additional_info,
    )
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)

    try:
        fetch_and_cache_historical_data(new_scenario.id, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return new_scenario


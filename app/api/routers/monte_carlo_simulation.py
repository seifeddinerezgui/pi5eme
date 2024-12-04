from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from app.database import get_db
from app.models import Portfolio, Transaction, User
from datetime import datetime

router = APIRouter()

# Value-at-Risk Calculation Function
def calculate_daily_returns(transactions):
    # Ensure transactions are sorted by date
    transactions.sort(key=lambda x: x.created_at)

    # Extract prices and calculate returns based on price changes
    prices = [txn.price for txn in transactions]
    returns = pd.Series(prices).pct_change().dropna()
    return returns

def simulate_portfolio_outcomes(initial_value, returns, num_simulations, time_horizon):
    simulations = []
    mean_return = returns.mean()
    std_dev = returns.std()

    for _ in range(num_simulations):
        portfolio_values = [initial_value]
        for _ in range(time_horizon):
            simulated_return = np.random.normal(mean_return, std_dev)
            next_value = portfolio_values[-1] * (1 + simulated_return)
            portfolio_values.append(next_value)
        simulations.append(portfolio_values)

    return pd.DataFrame(simulations).T

@router.get("/montecarlo/{user_id}")
def monte_carlo_simulation(user_id: int, num_simulations: int = 1000, time_horizon: int = 252, db: Session = Depends(get_db)):
    # Fetch user's portfolio balance
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Query all transactions
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user")

    # Calculate daily returns from transaction data
    returns = calculate_daily_returns(transactions)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Insufficient data for VaR calculation")

    # Run Monte Carlo simulation
    initial_value = portfolio.balance
    simulation_results = simulate_portfolio_outcomes(initial_value, returns, num_simulations, time_horizon)

    # Calculate summary statistics for visualization
    final_values = simulation_results.iloc[-1]
    avg_return = final_values.mean()
    var_95 = np.percentile(final_values, 5)  # 5th percentile for VaR at 95% confidence

    return {
        "avg_expected_return": avg_return,
        "value_at_risk_95": initial_value - var_95,
        "simulations": simulation_results.to_dict(orient="list")
    }

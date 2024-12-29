from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
import datetime as dt
from typing import List, Dict
from app.database import get_db
from app.models import Portfolio, Transaction, User
from app.api.routers.marketdata import router as marketdata_router

# FastAPI Router for Monte Carlo Simulation
router = APIRouter()
router.include_router(marketdata_router, prefix="/marketdata")

class MonteCarloParams(BaseModel):
    user_id: int
    start_date: dt.datetime
    end_date: dt.datetime
    num_simulations: int
    time_horizon: int
    cvar_alpha: float
    var_alpha: float

class MonteCarloResponse(BaseModel):
    avg_expected_return: float
    value_at_risk_95: float
    conditional_var: float
    simulations: Dict[int, List[float]]

class MonteCarloSimulator:

    def __init__(self, cvar_alpha: float, var_alpha: float):
        self.stocks = {}
        self.init_cash = 0
        self.cvar_alpha = cvar_alpha
        self.var_alpha = var_alpha
        self.pct_mean_return = None
        self.pct_cov_matrix = None
        self.portfolio_returns = None

    def get_portfolio(self, portfolio: Portfolio, start_time: dt.datetime, end_time: dt.datetime) -> None:
        stocks = list(portfolio.stocks.keys())
        stocks_data = marketdata_router.get_historical_data(stocks)  # Updated to use marketdata router
        
        stocks_data = stocks_data['Close'].dropna()
        pct_return = stocks_data.pct_change().dropna()
        self.pct_mean_return = pct_return.mean()
        self.pct_cov_matrix = pct_return.cov()
        self.init_cash = portfolio.book_amount
        self._get_weights(portfolio)

    def _get_weights(self, portfolio: Portfolio):
        total_book_cost = 0
        for stock in portfolio.stocks.keys():
            self.stocks[stock] = portfolio.stocks[stock].get_book_cost()
            total_book_cost += self.stocks[stock]

        for stock in portfolio.stocks.keys():
            self.stocks[stock] = self.stocks[stock] / total_book_cost

    def apply_monte_carlo(self, num_simulations: int, time_horizon: int) -> None:
        weights = np.array(list(self.stocks.values()), dtype=np.float64)
        mean_matrix = np.full((time_horizon, len(weights)), self.pct_mean_return).T
        portfolio_returns = np.zeros((time_horizon, num_simulations), dtype=np.float64)

        for sim in range(num_simulations):
            Z = np.random.normal(size=(time_horizon, len(weights)))
            L = np.linalg.cholesky(self.pct_cov_matrix)
            daily_returns = mean_matrix + np.inner(L, Z)
            portfolio_returns[:, sim] = np.cumprod(np.inner(weights, daily_returns.T) + 1) * self.init_cash

        self.portfolio_returns = portfolio_returns

    def get_var(self) -> float:
        if self.portfolio_returns is None:
            raise Exception("No Monte Carlo simulation has been applied")
        var = np.quantile(self.portfolio_returns[-1, :], self.var_alpha)
        return var

    def get_cvar(self) -> float:
        if self.portfolio_returns is None:
            raise Exception("No Monte Carlo simulation has been applied")
        var = self.get_var()
        cvar = np.mean(self.portfolio_returns[-1, self.portfolio_returns[-1, :] < var])
        return cvar

@router.post("/montecarlo", response_model=MonteCarloResponse)
def monte_carlo_simulation(params: MonteCarloParams, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == params.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    portfolio = db.query(Portfolio).filter(Portfolio.user_id == params.user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    simulator = MonteCarloSimulator(cvar_alpha=params.cvar_alpha, var_alpha=params.var_alpha)
    simulator.get_portfolio(portfolio, params.start_date, params.end_date)
    simulator.apply_monte_carlo(params.num_simulations, params.time_horizon)

    final_values = simulator.portfolio_returns[-1]
    avg_return = final_values.mean()
    var_95 = simulator.get_var()
    cvar_95 = simulator.get_cvar()

    simulations_dict = {i: simulator.portfolio_returns[:, i].tolist() for i in range(params.num_simulations)}

    return MonteCarloResponse(
        avg_expected_return=avg_return,
        value_at_risk_95=var_95,
        conditional_var=cvar_95,
        simulations=simulations_dict
    )

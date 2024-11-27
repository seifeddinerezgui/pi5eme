# services/VarCalculatorService.py

import numpy as np
from app.api.routers.marketdata import get_historical_data

def calculate_var_historical(returns, portfolio_balance, confidence_level=0.95):
    """
    Calculate Value-at-Risk (VaR) using the historical method and scale it by portfolio balance.

    Parameters:
    - returns: A list of past returns (daily or periodic returns).
    - portfolio_balance: The user's portfolio balance.
    - confidence_level: The confidence level for VaR (e.g., 0.95 for 95%).

    Returns:
    - Scaled VaR value.
    """
    # Sort returns in ascending order
    sorted_returns = np.sort(returns)
    # Determine the index for the VaR confidence level
    index = int((1 - confidence_level) * len(sorted_returns))
    # Calculate VaR and scale by portfolio balance
    var_value = abs(sorted_returns[index]) * portfolio_balance
    return var_value

class VarCalculatorService:
    
    @staticmethod
    def get_historical_returns(symbol: str):
        # Fetch historical data for the symbol
        historical_data = get_historical_data(symbol)
        
        # Extract closing prices
        closing_prices = [day['close'] for day in historical_data]
        
        # Calculate daily logarithmic returns
        returns = np.log(np.array(closing_prices[1:]) / np.array(closing_prices[:-1]))
        return returns.tolist()

    @staticmethod
    def calculate_var(symbol: str, portfolio_balance: float, confidence_level: float = 0.95):
        # Get returns for the symbol
        returns = VarCalculatorService.get_historical_returns(symbol)
        
        # Calculate VaR using the historical method, scaled by portfolio balance
        var_value = calculate_var_historical(returns, portfolio_balance, confidence_level=confidence_level)
        return var_value

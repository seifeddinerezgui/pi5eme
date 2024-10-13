# main.py
from fastapi import FastAPI, HTTPException
import httpx
import numpy as np
import pandas as pd
import uvicorn


app = FastAPI()

# Replace with your Marketstack API key
API_KEY = "8078ed800d7407105e179596b208a4ac"

def calculate_volatility(prices):
    return np.std(prices) * np.sqrt(252)  # Annualized volatility

def calculate_beta(stock_returns, market_returns):
    covariance = np.cov(stock_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)
    return covariance / market_variance

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns)

def interpret_metrics(volatility, beta, sharpe_ratio):
    interpretations = {}
    recommendations = []

    # Interpret volatility
    if volatility < 0.15:
        interpretations['volatility'] = "Low volatility indicates less risk."
        recommendations.append("Consider investing for stability.")
    elif volatility < 0.3:
        interpretations['volatility'] = "Moderate volatility indicates some risk."
        recommendations.append("This stock could be suitable for a balanced portfolio.")
    else:
        interpretations['volatility'] = "High volatility indicates higher risk."
        recommendations.append("This stock may be suitable for aggressive investors.")

    # Interpret beta
    if beta < 1:
        interpretations['beta'] = "Lower than market risk."
        recommendations.append("Good for conservative investors.")
    elif beta == 1:
        interpretations['beta'] = "Market-level risk."
        recommendations.append("Generally, an average investment choice.")
    else:
        interpretations['beta'] = "Higher than market risk."
        recommendations.append("Consider this stock if seeking high returns, but be aware of increased risk.")

    # Interpret Sharpe Ratio
    if sharpe_ratio < 1:
        interpretations['sharpe_ratio'] = "Suboptimal risk-adjusted return."
        recommendations.append("Consider looking for better investment opportunities.")
    elif sharpe_ratio < 2:
        interpretations['sharpe_ratio'] = "Acceptable risk-adjusted return."
        recommendations.append("This stock is a reasonable investment choice.")
    else:
        interpretations['sharpe_ratio'] = "Excellent risk-adjusted return."
        recommendations.append("Highly recommended for investment.")

    return interpretations, recommendations

@app.get("/risk-assessment/{ticker}")
async def risk_assessment(ticker: str, timeframe: str = "1year"):
    url = f"http://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols={ticker}&limit=365"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error retrieving data")
    
    data = response.json()
    if not data.get("data"):
        raise HTTPException(status_code=404, detail="Ticker not found")

    prices = [item["close"] for item in data["data"]]
    dates = [item["date"] for item in data["data"]]
    
    # Convert prices to a DataFrame for calculations
    prices_df = pd.DataFrame(prices, columns=["Close"], index=pd.to_datetime(dates))
    returns = prices_df["Close"].pct_change().dropna()
    
    # Calculate metrics
    volatility = calculate_volatility(prices)
    market_returns = np.random.normal(0.001, 0.01, len(returns))  # Simulated market returns for calculation
    beta = calculate_beta(returns, market_returns)
    sharpe_ratio = calculate_sharpe_ratio(returns)

    # Interpret results
    interpretations, recommendations = interpret_metrics(volatility, beta, sharpe_ratio)

    return {
        "ticker": ticker,
        "volatility": volatility,
        "beta": beta,
        "sharpe_ratio": sharpe_ratio,
        "interpretations": interpretations,
        "recommendations": recommendations,
        #"last_price": prices[-1]
    }

# To run the application, use the command: uvicorn main:app --reload



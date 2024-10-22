from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

import yfinance as yf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
import uvicorn
import ta
from typing import Optional

router=APIRouter()

def calculate_moving_average(data, window):
    return data['Close'].rolling(window=window).mean()

def calculate_rsi(data, window=14):
    return ta.momentum.RSIIndicator(data['Close'], window=window).rsi()

def calculate_bollinger_bands(data, window=20):
    indicator_bb = ta.volatility.BollingerBands(close=data["Close"], window=window, window_dev=2)
    data['bb_mavg'] = indicator_bb.bollinger_mavg()
    data['bb_upper'] = indicator_bb.bollinger_hband()
    data['bb_lower'] = indicator_bb.bollinger_lband()
    return data

def generate_trading_signal(data):
    """
    Generates individual strategy recommendations and an overall trading suggestion.
    """
    # Moving Average Strategy: Compare 50-day MA with 200-day MA
    short_ma = calculate_moving_average(data, 50)
    long_ma = calculate_moving_average(data, 200)

    # RSI Strategy: RSI above 70 is overbought, below 30 is oversold.
    rsi = calculate_rsi(data)

    # Bollinger Bands Strategy
    data = calculate_bollinger_bands(data)

    # Moving Averages recommendation
    if short_ma.iloc[-1] > long_ma.iloc[-1]:
        ma_signal = "Buy"
    elif short_ma.iloc[-1] < long_ma.iloc[-1]:
        ma_signal = "Sell"
    else:
        ma_signal = "Hold"

    # RSI recommendation
    if rsi.iloc[-1] < 30:
        rsi_signal = "Buy"
    elif rsi.iloc[-1] > 70:
        rsi_signal = "Sell"
    else:
        rsi_signal = "Hold"

    # Bollinger Bands recommendation
    if data['Close'].iloc[-1] < data['bb_lower'].iloc[-1]:
        bb_signal = "Buy"
    elif data['Close'].iloc[-1] > data['bb_upper'].iloc[-1]:
        bb_signal = "Sell"
    else:
        bb_signal = "Hold"

    # Overall recommendation logic
    recommendations = [ma_signal, rsi_signal, bb_signal]
    if recommendations.count("Buy") > recommendations.count("Sell"):
        overall_signal = "Buy"
    elif recommendations.count("Sell") > recommendations.count("Buy"):
        overall_signal = "Sell"
    else:
        overall_signal = "Hold"

    return ma_signal, rsi_signal, bb_signal, overall_signal

class StockRequest(BaseModel):
    ticker: str
    prediction_days: Optional[int] = 60

@router.post("/trading_strategy/")
async def get_trading_strategy(request: StockRequest):
    ticker = request.ticker
    prediction_days = request.prediction_days

    # Load data
    data = yf.download(ticker, start='2020-01-01', end='2024-10-01')
    
    if data.empty:
        return {"error": "No data found for the given ticker"}

    # Generate trading signal and technical indicators
    ma_signal, rsi_signal, bb_signal, overall_signal = generate_trading_signal(data)

    # Build the response
    return {
        "ticker": ticker,
        "moving_average_strategy": ma_signal,
        "rsi_strategy": rsi_signal,
        "bollinger_bands_strategy": bb_signal,
        "overall_recommendation": overall_signal
    }


from fastapi import FastAPI, HTTPException
import finnhub

# Initialize the Finnhub client
finnhub_client = finnhub.Client(api_key="cs5c8u9r01qo1hu1debgcs5c8u9r01qo1hu1dec0")

# Fetch recommendation trends for a given ticker
@router.get("/recommendation/{ticker}")
def get_recommendation_trends(ticker: str):
    try:
        # Call Finnhub API to get recommendation trends
        recommendation_trends = finnhub_client.recommendation_trends(ticker)
        
        if not recommendation_trends:
            raise HTTPException(status_code=404, detail="No recommendation trends found for this ticker")
        
        return recommendation_trends

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Run the app with: uvicorn script_name:app --reload




import json
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
import uvicorn
import ta
from typing import Optional
import os

router = APIRouter()
DATA_FILE = "trading_data.json"

def load_data():
    """Load data from JSON file, if it exists."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

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
    short_ma = calculate_moving_average(data, 50)
    long_ma = calculate_moving_average(data, 200)
    rsi = calculate_rsi(data)
    data = calculate_bollinger_bands(data)

    if short_ma.iloc[-1] > long_ma.iloc[-1]:
        ma_signal = "Buy"
    elif short_ma.iloc[-1] < long_ma.iloc[-1]:
        ma_signal = "Sell"
    else:
        ma_signal = "Hold"

    if rsi.iloc[-1] < 30:
        rsi_signal = "Buy"
    elif rsi.iloc[-1] > 70:
        rsi_signal = "Sell"
    else:
        rsi_signal = "Hold"

    if data['Close'].iloc[-1] < data['bb_lower'].iloc[-1]:
        bb_signal = "Buy"
    elif data['Close'].iloc[-1] > data['bb_upper'].iloc[-1]:
        bb_signal = "Sell"
    else:
        bb_signal = "Hold"

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
    data_store = load_data()

    # Check if ticker data already exists in JSON file
    if ticker in data_store:
        return data_store[ticker]

    # Fetch new data if not found in the JSON file
    data = yf.download(ticker, start='2020-01-01', end='2024-10-01')
    if data.empty:
        return {"error": "No data found for the given ticker"}

    # Generate trading signals and technical indicators
    ma_signal, rsi_signal, bb_signal, overall_signal = generate_trading_signal(data)

    result = {
        "ticker": ticker,
        "moving_average_strategy": ma_signal,
        "rsi_strategy": rsi_signal,
        "bollinger_bands_strategy": bb_signal,
        "overall_recommendation": overall_signal
    }

    # Save the new result in the JSON file
    data_store[ticker] = result
    save_data(data_store)

    return result

import finnhub

finnhub_client = finnhub.Client(api_key="cs5c8u9r01qo1hu1debgcs5c8u9r01qo1hu1dec0")

@router.get("/recommendation/{ticker}")
def get_recommendation_trends(ticker: str):
    data_store = load_data()

    # Check if recommendation data already exists
    if ticker in data_store and "recommendation" in data_store[ticker]:
        return data_store[ticker]["recommendation"]

    try:
        recommendation_trends = finnhub_client.recommendation_trends(ticker)
        if not recommendation_trends:
            raise HTTPException(status_code=404, detail="No recommendation trends found for this ticker")

        # Save recommendation trends in JSON file
        if ticker not in data_store:
            data_store[ticker] = {}
        data_store[ticker]["recommendation"] = recommendation_trends
        save_data(data_store)

        return recommendation_trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

app = FastAPI()
app.include_router(router)

# Run the app with: uvicorn script_name:app --reload

from fastapi import HTTPException, APIRouter
from prophet import Prophet
from pydantic import BaseModel
import yfinance as yf
from typing import List, Dict
from datetime import date
import pandas as pd

router = APIRouter()


START = "2020-01-01"
END = date.today().strftime("%Y-%m-%d")

class ForecastRequest(BaseModel):
    symbol: str
    years: int

@router.get("/stocks/")
def get_available_stocks():
    """Provide a list of stocks available for forecasting."""
    return ["AAPL", "GOOG", "MSFT", "GME", "AMZN", "TSLA"]

@router.post("/forecast/")
def get_forecast(data: ForecastRequest):
    """Fetch stock data and provide forecast."""
    try:
        # Load stock data from Yahoo Finance
        df = yf.download(data.symbol, START, END)
        df.reset_index(inplace=True)

        # Prepare the data for Prophet
        df_train = df[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
        model = Prophet()
        model.fit(df_train)

        # Forecast for the given period
        future = model.make_future_dataframe(periods=data.years * 365)
        forecast = model.predict(future)

        # Format the result for frontend consumption
        forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records')
        return {
            "historical": df.to_dict(orient='records'),
            "forecast": forecast_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast: {str(e)}")

import requests
from fastapi import HTTPException

class MarketDataService:
    API_URL = "https://www.alphavantage.co/query"
    API_KEY = "4N92KPXVO2CT7UTA"

    @classmethod
    def get_market_data(cls, symbol: str) -> float:
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "5min",
            "apikey": cls.API_KEY
        }
        response = requests.get(cls.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            # Check if the response contains an error message
            if "Error Message" in data:
                raise HTTPException(status_code=400, detail=f"Error from Alpha Vantage API: {data['Error Message']}")

            # Check if the time series data is available
            time_series = data.get("Time Series (5min)")
            if time_series:
                # Get the latest timestamp and data
                latest_timestamp = sorted(time_series.keys())[-1]
                latest_data = time_series[latest_timestamp]

                # Extract the closing price as a float
                return float(latest_data["4. close"])
            else:
                # Log the full response if the expected data is not found
                raise HTTPException(status_code=404, detail=f"Time Series data not found. Full response: {data}")
        else:
            # Log any non-200 responses from the API
            raise HTTPException(status_code=response.status_code, detail=f"Error calling Alpha Vantage API. Full response: {response.json()}")

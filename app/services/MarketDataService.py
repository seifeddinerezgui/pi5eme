import requests
from fastapi import HTTPException

class MarketDataService:
    API_URL = "https://financialmodelingprep.com/api/v3/quote"
    API_KEY = "hzlBlPFOVkNATY9eOYfij1UvlZS6k95N"

    @classmethod
    def get_market_data(cls, symbol: str) -> float:
        """Fetches the latest stock price for a given symbol."""
        url = f"{cls.API_URL}/{symbol}?apikey={cls.API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Check if the response contains data
            if data:
                # The latest price can be found in the "price" field
                latest_data = data[0]
                return float(latest_data.get("price"))
            else:
                # Log the full response if the expected data is not found
                raise HTTPException(status_code=404, detail=f"Price data not found. Full response: {data}")
        else:
            # Log any non-200 responses from the API
            raise HTTPException(status_code=response.status_code, detail=f"Error calling FMP API. Full response: {response.json()}")

import requests
from fastapi import HTTPException

class MarketDataService1:
    API_URL = "https://www.alphavantage.co/query"
    API_KEY = "8F7BODH259SP28AQ"

    @classmethod
    def get_market_data(cls, symbol: str) -> float:
        """
        Récupère le dernier prix du marché pour un symbole donné afin de passer un ordre d'achat ou de vente.
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": "5min",  # Intervalle par défaut pour obtenir le dernier prix
            "apikey": cls.API_KEY
        }
        response = requests.get(cls.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            # Vérifier si la réponse contient un message d'erreur
            if "Error Message" in data:
                raise HTTPException(status_code=400, detail=f"Erreur depuis l'API Alpha Vantage: {data['Error Message']}")

            # Extraire la série temporelle
            time_series = data.get("Time Series (5min)")
            if time_series:
                # Obtenir la dernière entrée temporelle et extraire le prix de clôture
                latest_timestamp = sorted(time_series.keys())[-1]
                latest_data = time_series[latest_timestamp]
                return float(latest_data["4. close"])  # Dernier prix de clôture
            else:
                raise HTTPException(status_code=404, detail="Données de série temporelle introuvables")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Erreur de l'API Alpha Vantage. Réponse complète: {response.json()}")

    @classmethod
    def get_market_data1(cls, symbol: str, interval: str):
        """
        Récupère les données de marché en fonction de l'intervalle pour afficher les courbes.
        Si l'intervalle est inférieur ou égal à '1d', récupère les données intrajournalières.
        Pour d'autres intervalles, récupère les données historiques journalières.
        """
        if interval in ["1min", "5min", "15min", "30min", "60min"]:
            return cls.get_intraday_data(symbol, interval)
        elif interval == "1d":
            return cls.get_historical_data(symbol)
        else:
            raise HTTPException(status_code=400, detail="Intervalle invalide")

    @classmethod
    def get_intraday_data(cls, symbol: str, interval: str):
        """
        Récupère les données intrajournalières d'Alpha Vantage en fonction de l'intervalle (5min, 15min, etc.)
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": cls.API_KEY
        }
        response = requests.get(cls.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            # Vérifier la présence d'un message d'erreur
            if "Error Message" in data:
                raise HTTPException(status_code=400, detail=f"Erreur depuis l'API Alpha Vantage: {data['Error Message']}")

            time_series_key = f"Time Series ({interval})"
            time_series = data.get(time_series_key)

            if time_series:
                # Retourner les données les plus récentes, triées par heure
                return {time: time_series[time] for time in sorted(time_series.keys(), reverse=True)}
            else:
                raise HTTPException(status_code=404, detail="Données de série temporelle intrajournalières introuvables")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erreur de l'API Alpha Vantage")

    @classmethod
    def get_historical_data(cls, symbol: str):
        """
        Récupère les données historiques (série journalière) depuis Alpha Vantage.
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": cls.API_KEY,
            "outputsize": "compact"  # Utiliser "full" pour obtenir plus de données (jusqu'à 20 ans)
        }
        response = requests.get(cls.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            # Vérifier si la série journalière est présente
            if "Time Series (Daily)" in data:
                return {date: data["Time Series (Daily)"][date] for date in sorted(data["Time Series (Daily)"].keys(), reverse=True)}
            else:
                raise HTTPException(status_code=404, detail="Données historiques introuvables")
        else:
            raise HTTPException(status_code=response.status_code, detail="Erreur de l'API Alpha Vantage")

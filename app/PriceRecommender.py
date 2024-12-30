import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from app.services.MarketDataService1 import MarketDataService1

class PriceRecommender:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data_fetcher = MarketDataService1()
        self.historical_data = self.data_fetcher.get_historical_data(symbol)

        # Afficher les données historiques récupérées
        print("Données historiques récupérées :", self.historical_data)

        # Convertir les données historiques en DataFrame
        self.df = pd.DataFrame(self.historical_data).T

        # Renommer les colonnes pour faciliter l'accès
        self.df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume'
        }, inplace=True)

        # Afficher les colonnes disponibles dans le DataFrame
        print("Colonnes dans le DataFrame :", self.df.columns)

        # Vérification des colonnes
        if 'close' not in self.df.columns:
            raise KeyError("'close' column is missing from the DataFrame")

        self.df['close'] = self.df['close'].astype(float)
        self.df['date'] = pd.to_datetime(self.df.index)
        self.df.set_index('date', inplace=True)

    def train_model(self):
        # Préparer les données
        self.df['target'] = self.df['close'].shift(-1)  # Prédire le prix du jour suivant
        X = np.array(range(len(self.df))).reshape(-1, 1)  # Indice des jours
        y = self.df['target'].dropna()

        model = LinearRegression()
        model.fit(X[:-1], y)  # Exclure la dernière valeur car elle n'a pas de cible

        return model

    def predict_next_price(self):
        model = self.train_model()
        next_day_index = np.array([[len(self.df)]])  # Prochaine journée
        predicted_price = model.predict(next_day_index)[0]

        return predicted_price

    def calculate_recommendation(self):
        current_price = self.df['close'].iloc[-1]
        predicted_price = self.predict_next_price()

        if predicted_price > current_price:
            recommendation = "Acheter"
        else:
            recommendation = "Vendre"

        return {
            "current_price": current_price,
            "predicted_price": predicted_price,
            "recommendation": recommendation
        }

# Exemple d'utilisation


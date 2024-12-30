import time
import numpy as np
from fastapi import HTTPException

from app.services.MarketDataService1 import MarketDataService1


class SimpleMovingAverageStrategy:
    def __init__(self, symbol: str, short_window: int = 50, long_window: int = 200):
        """
        Initialise la stratégie avec un symbole et des fenêtres pour les moyennes mobiles.
        :param symbol: Le symbole de l'action (ex. "AAPL", "GOOG").
        :param short_window: La fenêtre pour la moyenne mobile courte.
        :param long_window: La fenêtre pour la moyenne mobile longue.
        """
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.market_data_service = MarketDataService1

    def calculate_moving_average(self, data: dict, window: int) -> np.ndarray:
        """
        Calcule la moyenne mobile d'une série de données.
        :param data: La série temporelle des prix de clôture.
        :param window: La taille de la fenêtre pour la moyenne mobile.
        :return: La moyenne mobile calculée.
        """
        prices = [float(entry["4. close"]) for entry in data.values()]
        return np.convolve(prices, np.ones(window), 'valid') / window

    def check_trade_signal(self, short_ma: np.ndarray, long_ma: np.ndarray) -> str:
        """
        Vérifie si un signal d'achat ou de vente est généré en fonction des moyennes mobiles.
        :param short_ma: La moyenne mobile courte.
        :param long_ma: La moyenne mobile longue.
        :return: "buy", "sell" ou "hold" selon le signal.
        """
        if short_ma[-1] > long_ma[-1]:
            return "buy"  # Signal d'achat lorsque la moyenne mobile courte est au-dessus de la longue
        elif short_ma[-1] < long_ma[-1]:
            return "sell"  # Signal de vente lorsque la moyenne mobile courte est en dessous de la longue
        else:
            return "hold"  # Pas de signal lorsque les moyennes mobiles se croisent

    def execute_strategy(self, interval: str = "5min") -> str:
        """
        Exécute la stratégie en récupérant les données de marché et en appliquant la logique de trading.
        :param interval: L'intervalle des données (ex. "5min", "15min").
        :return: Le signal d'achat/vente (buy, sell, hold).
        """
        try:
            # Récupérer les données de marché
            market_data = self.market_data_service.get_market_data1(self.symbol, interval)

            # Calculer les moyennes mobiles courtes et longues
            short_ma = self.calculate_moving_average(market_data, self.short_window)
            long_ma = self.calculate_moving_average(market_data, self.long_window)

            # Vérifier les signaux de trading
            signal = self.check_trade_signal(short_ma, long_ma)

            return signal
        except HTTPException as e:
            return f"Erreur dans la récupération des données: {str(e)}"

    def run_strategy(self, interval: str = "5min", delay: int = 60) -> None:
        """
        Exécute la stratégie de manière répétée à intervalles réguliers.
        :param interval: L'intervalle des données (par exemple, "5min").
        :param delay: Le délai entre les exécutions de la stratégie, en secondes.
        """
        while True:
            signal = self.execute_strategy(interval)
            print(f"Signal de trading pour {self.symbol}: {signal}")
            time.sleep(delay)  # Attendre avant de réexécuter la stratégie

# Exemple d'utilisation
if __name__ == "__main__":
    strategy = SimpleMovingAverageStrategy(symbol="AAPL", short_window=50, long_window=200)
    strategy.run_strategy(interval="5min", delay=300)  # Vérifier toutes les 5 minutes

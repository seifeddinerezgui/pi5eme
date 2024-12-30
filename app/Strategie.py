import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

class Strategy:
    # Fonction pour calculer le RSI (Relative Strength Index)
    @staticmethod
    def calculate_rsi(data, window=14):
        delta = data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # Fonction pour calculer la taille de position
    @staticmethod
    def calculate_position_size(account_balance, risk_percentage, current_price):
        risk_amount = account_balance * risk_percentage
        position_size = risk_amount / current_price
        return position_size

    # Fonction principale pour la stratégie de trading de momentum
    @staticmethod
    def momentum_strategy(stock_ticker, start_date, end_date, account_balance):
        # Récupérer les données historiques du stock
        data = yf.download(stock_ticker, start=start_date, end=end_date)

        # Calculer le RSI
        data['RSI'] = Strategy.calculate_rsi(data)

        # Calculer les moyennes mobiles
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()

        # Définir les seuils pour les signaux d'achat et de vente
        overbought = 70
        oversold = 30

        # Initialiser les positions
        data['Position'] = 0
        data['Entry_Price'] = np.nan
        data['Stop_Loss'] = np.nan
        data['Take_Profit'] = np.nan

        # Paramètres de gestion des risques
        risk_percentage = 0.01  # Risque de 1% du solde du compte par trade
        trailing_percentage = 0.02  # Trailing stop de 2%

        # Boucle à travers les données pour déterminer les positions
        for i in range(1, len(data)):
            if data['RSI'].iloc[i] < oversold and data['Position'].iloc[i-1] == 0:
                # Signal d'achat
                position_size = Strategy.calculate_position_size(account_balance, risk_percentage, data['Close'].iloc[i])
                data['Position'].iloc[i] = 1  # Acheter
                data['Entry_Price'].iloc[i] = data['Close'].iloc[i]
                data['Stop_Loss'].iloc[i] = data['Entry_Price'].iloc[i] * (1 - 0.02)  # 2% stop loss
                data['Take_Profit'].iloc[i] = data['Entry_Price'].iloc[i] * (1 + 0.05)  # 5% take profit
            elif data['RSI'].iloc[i] > overbought and data['Position'].iloc[i-1] == 1:
                # Signal de vente
                data['Position'].iloc[i] = -1  # Vendre
            else:
                # Conserver la position précédente
                data['Position'].iloc[i] = data['Position'].iloc[i-1]

            # Mise à jour du stop loss dynamique
            if data['Position'].iloc[i] == 1:
                data['Stop_Loss'].iloc[i] = max(data['Stop_Loss'].iloc[i-1], data['Close'].iloc[i] * (1 - trailing_percentage))
                if data['Close'].iloc[i] >= data['Take_Profit'].iloc[i-1]:
                    data['Position'].iloc[i] = 0  # Prendre les bénéfices
            elif data['Position'].iloc[i] == -1:
                data['Entry_Price'].iloc[i] = np.nan  # Réinitialiser le prix d'entrée sur vente

        # Calculer les retours
        data['Daily_Return'] = data['Close'].pct_change()
        data['Strategy_Return'] = data['Daily_Return'] * data['Position'].shift(1)

        # Calculer les retours cumulés
        data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()
        data['Cumulative_Market_Return'] = (1 + data['Daily_Return']).cumprod()

        # Visualiser les résultats
        plt.figure(figsize=(14, 7))
        plt.plot(data['Cumulative_Return'], label='Retour de la stratégie', color='blue')
        plt.plot(data['Cumulative_Market_Return'], label='Retour du marché', color='orange')
        plt.scatter(data.index[data['Position'] == 1], data[data['Position'] == 1]['Close'], label='Achat', marker='^', color='g')
        plt.scatter(data.index[data['Position'] == -1], data[data['Position'] == -1]['Close'], label='Vente', marker='v', color='r')
        plt.title(f'Stratégie de Trading de Momentum pour {stock_ticker}')
        plt.xlabel('Date')
        plt.ylabel('Retour cumulatif')
        plt.legend()
        plt.grid()
        plt.show()

from fastapi import APIRouter, HTTPException
from typing import Optional
import pandas as pd
from pydantic import BaseModel

from app.services.MarketDataService1 import MarketDataService1

router = APIRouter()


class TradingStrategyRequest(BaseModel):
    symbol: str
    short_window: int = 50  # Période pour la moyenne mobile courte (par défaut 50)
    long_window: int = 200  # Période pour la moyenne mobile longue (par défaut 200)


@router.get("/strategy/trading_signal")
async def get_trading_signal(request: TradingStrategyRequest):
    """
    Applique une stratégie de trading basée sur la moyenne mobile (SMA)
    :param symbol: Le symbole de l'action (ex: 'AAPL')
    :param short_window: Période de la moyenne mobile courte
    :param long_window: Période de la moyenne mobile longue
    """
    try:
        # Récupération des données de marché
        data = MarketDataService1.get_market_data1(request.symbol, interval="1d")

        # Conversion des données dans un format exploitable
        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.sort_index(ascending=True)  # Trier les données par date croissante
        df["close"] = pd.to_numeric(df["4. close"])  # Convertir la colonne de prix de clôture

        # Calcul des moyennes mobiles
        df['short_sma'] = df['close'].rolling(window=request.short_window).mean()
        df['long_sma'] = df['close'].rolling(window=request.long_window).mean()

        # Vérification du signal de trading
        signal = None
        last_short_sma = df['short_sma'].iloc[-1]
        last_long_sma = df['long_sma'].iloc[-1]

        if last_short_sma > last_long_sma:
            signal = "BUY"  # Si la SMA courte est au-dessus de la SMA longue, on achète
        elif last_short_sma < last_long_sma:
            signal = "SELL"  # Si la SMA courte est en dessous de la SMA longue, on vend
        else:
            signal = "HOLD"  # Sinon, on maintient la position

        return {"symbol": request.symbol, "signal": signal, "last_short_sma": last_short_sma,
                "last_long_sma": last_long_sma}

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dans l'exécution de la stratégie: {str(e)}")

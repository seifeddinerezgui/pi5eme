from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, LSTM
import os

app = FastAPI()
router = APIRouter()

scaler = MinMaxScaler(feature_range=(0, 1))
prediction_days = 60
models_dir = "models"  # Dossier où seront stockés les modèles

# Crée le dossier si nécessaire
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

# Fonction pour construire et entraîner le modèle
def build_and_train_model(company):
    start = dt.datetime(2019, 1, 1)
    end = dt.datetime(2024, 8, 1)
    
    data = yf.download(company, start=start, end=end)
    if data.empty:
        return "No data found."
    
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    X_train = []
    Y_train = []

    for X in range(prediction_days, len(scaled_data)):
        X_train.append(scaled_data[X - prediction_days:X, 0])
        Y_train.append(scaled_data[X, 0])

    X_train, Y_train = np.array(X_train), np.array(Y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, Y_train, epochs=25, batch_size=32)
    
    # Sauvegarde du modèle
    model_path = os.path.join(models_dir, f"{company}.h5")
    model.save(model_path)
    return model

# Modèle de données pour les requêtes
class StockRequest(BaseModel):
    company: str

# Endpoint de prédiction
@router.post("/predict/")
async def predict_next_day(stock: StockRequest):
    model_path = os.path.join(models_dir, f"{stock.company}.h5")

    # Check if a model already exists for this ticker
    if os.path.exists(model_path):
        # Load the saved model
        model = load_model(model_path)
    else:
        # If model doesn't exist, build and train it
        model = build_and_train_model(stock.company)
        if model == "No data found.":
            return {"error": "No data found for the given company."}

    # Define date range for test data
    test_start = dt.datetime(2020, 1, 1)
    test_end = dt.datetime.now()

    # Download historical data for the company
    data = yf.download(stock.company, start=test_start, end=test_end)
    if data.empty:
        return {"error": "No data found for the given company."}

    # Fit the scaler on the historical data
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    # Prepare input data for prediction
    model_inputs = scaled_data[-prediction_days:]  # Take the last 'prediction_days' values

    # Reshape the input to be compatible with LSTM model
    X_test = np.array([model_inputs[:, 0]])
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # Predict for the next day
    next_day_prediction = model.predict(X_test)
    next_day_prediction = scaler.inverse_transform(next_day_prediction)

    # Convert the result to JSON-compatible format
    next_day_price = float(next_day_prediction[0][0])

    return {"next_day_prediction": next_day_price}


# Ajout du router à l'app FastAPI
app.include_router(router)

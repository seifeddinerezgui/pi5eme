from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from fastapi import APIRouter
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
import uvicorn


router=APIRouter()

# Load the model globally (you can train it beforehand or dynamically in your code)
scaler = MinMaxScaler(feature_range=(0, 1))
model = None
prediction_days = 60

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

    global model
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
    return "Model trained successfully."


# Input Model
class StockRequest(BaseModel):
    company: str

@router.post("/predict/")
async def predict_next_day(stock: StockRequest):

    result = build_and_train_model(stock.company)
    if model is None:
        return {"error": "Model is not trained. Please call the /train endpoint first."}

    # Load test data
    test_start = dt.datetime(2020, 1, 1)
    test_end = dt.datetime.now()

    data = yf.download(stock.company, start=test_start, end=test_end)
    if data.empty:
        return {"error": "No data found for the given company."}

    actual_prices = data['Close'].values
    total_dataset = pd.concat((data['Close'], data['Close']), axis=0)

    # Prepare the data for the next day prediction
    model_inputs = total_dataset[len(total_dataset) - prediction_days:].values
    model_inputs = model_inputs.reshape(-1, 1)
    model_inputs = scaler.transform(model_inputs)

    # Prepare the data for the model to predict the next day
    X_test = [model_inputs[-prediction_days:, 0]]
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    # Make the prediction for the next day
    next_day_prediction = model.predict(X_test)
    next_day_prediction = scaler.inverse_transform(next_day_prediction)

    # Convert the NumPy float to a native Python float for JSON serialization
    next_day_price = float(next_day_prediction[0][0])

    # Return the next day's predicted price
    return {"next_day_prediction": next_day_price}





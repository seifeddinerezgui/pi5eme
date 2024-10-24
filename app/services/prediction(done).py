import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import datetime as dt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

def stock_prediction(company):
    # Load data
    start = dt.datetime(2017, 1, 1)
    end = dt.datetime(2024, 8, 1)
    
    data = yf.download(company, start=start, end=end)
    if data.empty:
        print("No data found. Check the company ticker or date range.")
        return
    else:
        print(f"Data for {company}:")
        print(data.head())  # Print the first few rows of data

    # Prepare data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

    prediction_days = 60

    X_train = []
    Y_train = []

    for X in range(prediction_days, len(scaled_data)):
        X_train.append(scaled_data[X - prediction_days:X, 0])
        Y_train.append(scaled_data[X, 0])

    X_train, Y_train = np.array(X_train), np.array(Y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Build the model
    model = Sequential()

    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))  # The prediction

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, Y_train, epochs=25, batch_size=32)

    # Test the model accuracy on existing data
    test_start = dt.datetime(2023, 1, 1)
    test_end = dt.datetime.now()

    test_data = yf.download(company, start=test_start, end=test_end)
    actual_prices = test_data['Close'].values

    total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)

    model_inputs = total_dataset[len(total_dataset) - len(test_data) - prediction_days:].values
    model_inputs = model_inputs.reshape(-1, 1)
    model_inputs = scaler.transform(model_inputs)

    # Make predictions on test data
    X_test = []

    for X in range(prediction_days, len(model_inputs)):
        X_test.append(model_inputs[X - prediction_days:X, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    predicted_prices = model.predict(X_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)

    # Plot the test predictions
    plt.plot(actual_prices, color="black", label="Actual Prices")
    plt.plot(predicted_prices, color='green', label="Predicted Prices")
    plt.title(f"{company} Share Price")
    plt.xlabel('Time')
    plt.ylabel(f'{company} Share Price')
    plt.legend()
    plt.show()

    # Predict the next day
    real_data = [model_inputs[len(model_inputs) + 1 - prediction_days:len(model_inputs + 1), 0]]
    real_data = np.array(real_data)
    real_data = np.reshape(real_data, (real_data.shape[0], real_data.shape[1], 1))

    prediction = model.predict(real_data)
    prediction = scaler.inverse_transform(prediction)
    print(f"Prediction for the next day: {prediction}")

# Example usage:
stock_prediction('META')

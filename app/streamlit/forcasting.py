import streamlit as st
import yfinance as yf
from datetime import date
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

START = "2020-01-01"
END = date.today().strftime("%Y-%m-%d")

st.title("Forecasting of Stock Prices")
stocks = ("AAPL", "GOOG", "MSFT", "GME", "AMZN", "TSLA")
selected_stock = st.selectbox("Select dataset for prediction", stocks)

n_years = st.slider("Years of prediction:", 1, 4)
period = n_years * 365

@st.cache_data
def load_data(ticker):
    """Load stock data from Yahoo Finance."""
    data = yf.download(ticker, START, END)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Loading data...")
data = load_data(selected_stock)
data_load_state.text("Loading data...done!")

st.subheader('Raw data')
st.write(data.tail())

def plot_raw_data():
    """Plot the raw stock data with an interactive slider."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='Stock Open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Stock Close'))
    fig.layout.update(
        title_text="Time Series Data with Rangeslider",
        xaxis_rangeslider_visible=True
    )
    st.plotly_chart(fig)

plot_raw_data()

# Forecasting with Prophet
df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
model = Prophet()
model.fit(df_train)

future = model.make_future_dataframe(periods=period)
forecast = model.predict(future)

st.subheader('Forecast Data')
st.write(forecast.tail())

st.write('Forecast Data Plot')
fig1 = plot_plotly(model, forecast)
st.plotly_chart(fig1)

st.write('Forecast Components')
fig2 = model.plot_components(forecast)
st.write(fig2)
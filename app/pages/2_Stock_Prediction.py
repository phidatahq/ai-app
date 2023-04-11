import datetime
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
import yfinance as yf
import streamlit as st

from prophet import Prophet
from streamlit.hello.utils import show_code

from workspace.settings import ws_settings

TODAY = datetime.date.today()
DEFAULT_TICKER = "GOOG"
DEFAULT_DAYS_TO_PREDICT = 21
MODELS_DIR = ws_settings.ws_root.joinpath("models")


def train(ticker: str = DEFAULT_TICKER) -> None:
    """Train a Prophet model and save to models directory"""

    data = yf.download(ticker, "2020-01-01", TODAY.strftime("%Y-%m-%d"))
    data["Adj Close"].plot(title=f"{ticker} Stock Adjusted Closing Price")

    df_forecast = data.copy()
    df_forecast.reset_index(inplace=True)
    df_forecast["ds"] = df_forecast["Date"]
    df_forecast["y"] = df_forecast["Adj Close"]
    df_forecast = df_forecast[["ds", "y"]]
    # df_forecast

    model = Prophet()
    model.fit(df_forecast)
    model_path = MODELS_DIR.joinpath(f"{ticker}_prediction.joblib")
    joblib.dump(model, model_path)
    st.session_state["model_trained"] = True
    st.session_state["model_path"] = model_path


def predict(ticker: str = DEFAULT_TICKER, days: int = DEFAULT_DAYS_TO_PREDICT):
    """Predict using a trained Prophet model"""

    model_file = MODELS_DIR.joinpath(f"{ticker}_prediction.joblib")
    if not model_file.exists():
        return None

    model = joblib.load(model_file)
    future = TODAY + datetime.timedelta(days=days)

    dates = pd.date_range(
        start="2020-01-01",
        end=future.strftime("%Y-%m-%d"),
    )
    df = pd.DataFrame({"ds": dates})

    forecast = model.predict(df)
    st.session_state["model_plot"] = model.plot(forecast)

    return forecast


#
# -*- Create Sidebar
#
def create_sidebar():
    st.sidebar.markdown("## Querybot Settings")

    st.sidebar.markdown("### Select a ticker")
    selected_ticker = st.sidebar.text_input("Ticker", DEFAULT_TICKER)
    selected_days = st.sidebar.slider(
        "Days to predict", 1, 365, DEFAULT_DAYS_TO_PREDICT
    )
    # store session state
    st.session_state["selected_ticker"] = selected_ticker
    st.session_state["selected_days"] = selected_days

    if st.sidebar.button("Train"):
        train(selected_ticker)

    if st.sidebar.button("Predict"):
        prediction_result = predict(selected_ticker, selected_days)
        st.session_state["prediction_result"] = prediction_result

    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Create Main Page
#
def create_main_page():
    st.markdown("## Predict stock price using time series forecasting")
    st.write(
        "This app uses [Prophet](https://facebook.github.io/prophet/) to predict stock price."
    )
    st.write("1. Train a model for the ticker using the button in the sidebar")
    st.write(
        "2. Predict the stock price for the next 21 days using the button in the sidebar"
    )
    st.markdown("---")

    model_trained = st.session_state.get("model_trained", False)
    if not model_trained:
        st.write("🦆  Click train button")
        return

    model_path = st.session_state.get("model_path", None)
    if model_path:
        st.write(f"🦆  Model: {Path(model_path).name}")

    prediction_result = st.session_state.get("prediction_result", None)
    if prediction_result is None:
        st.write("🦆  Click predict button")
        return

    if prediction_result is not None:
        st.write("🦆  Prediction Result")

    model_plot = st.session_state.get("model_plot", None)
    if model_plot is not None:
        st.write(st.session_state["model_plot"])

    _predicted_days = prediction_result.tail(st.session_state["selected_days"]).to_dict(
        "records"
    )
    _predictions_dict: Dict[str, List] = {"ds": [], "predicted_price": []}
    for row in _predicted_days:
        _predictions_dict["ds"].append(row["ds"].strftime("%m/%d/%Y"))
        _predictions_dict["predicted_price"].append(row["yhat"])

    _predictions_df = pd.DataFrame.from_dict(_predictions_dict)
    st.table(_predictions_df)


#
# -*- Run the app
#
create_sidebar()
create_main_page()

if st.sidebar.button("Show Code"):
    st.write("## Training Code")
    show_code(train)

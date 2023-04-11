from datetime import date
from pathlib import Path
from typing import List

import joblib
from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.endpoints import endpoints
from workspace.settings import ws_settings

from prophet import Prophet
import yfinance as yf

######################################################
## Router for Training Models
######################################################

training_router = APIRouter(prefix=endpoints.TRAIN, tags=["train"])

# -*- Default values for training
DEFAULT_TICKER: str = "GOOG"
MODELS_DIR: Path = ws_settings.ws_root.joinpath("models")


def train(ticker: str = DEFAULT_TICKER) -> None:
    """Train a Prophet model and save to the models directory"""

    data = yf.download(ticker, "2020-01-01", date.today().strftime("%Y-%m-%d"))

    df_forecast = data.copy()
    df_forecast.reset_index(inplace=True)
    df_forecast["ds"] = df_forecast["Date"]
    df_forecast["y"] = df_forecast["Adj Close"]
    df_forecast = df_forecast[["ds", "y"]]

    model = Prophet()
    model.fit(df_forecast)
    model_path = MODELS_DIR.joinpath(f"{ticker}_prediction.joblib")
    joblib.dump(model, model_path)


# -*- Pydantic models for training request and response
class TrainingRequest(BaseModel):
    tickers: List[str] = [DEFAULT_TICKER]


class TrainingResponse(BaseModel):
    trained_tickers: List[str]


@training_router.post("/ticker")
def train_stock_price(training_request: TrainingRequest):
    trained_tickers = []

    for ticker in training_request.tickers:
        try:
            train(ticker)
            trained_tickers.append(ticker)
        except Exception as e:
            print(f"Failed to train {ticker}: {e}")

    return TrainingResponse(trained_tickers=trained_tickers)

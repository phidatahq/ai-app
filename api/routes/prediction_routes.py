from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict

import joblib
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.training_routes import train
from api.routes.endpoints import endpoints
from workspace.settings import ws_settings

######################################################
## Router for Serving Predictions
######################################################

prediction_router = APIRouter(prefix=endpoints.PREDICT, tags=["predict"])

# -*- Default values for predictions
DEFAULT_TICKER: str = "GOOG"
DEFAULT_DAYS_TO_PREDICT: int = 21
MODELS_DIR: Path = ws_settings.ws_root.joinpath("models")

# -*- Load models for predictions
stock_prediction_models = {}
for model_file in MODELS_DIR.glob("*.joblib"):
    model_name = model_file.stem.split("_")[0]
    stock_prediction_models[model_name] = joblib.load(model_file)
    print(f"Loaded model: {model_name}")


def predict(
    ticker: str = DEFAULT_TICKER, days: int = DEFAULT_DAYS_TO_PREDICT
) -> List[Dict]:
    """Predict using a trained Prophet model"""

    model_file = MODELS_DIR.joinpath(f"{ticker}_prediction.joblib")
    if not model_file.exists():
        print(f"Training model: {ticker}")
        train(ticker)

    if not model_file.exists():
        raise Exception(f"Model not found: {ticker}")

    model = joblib.load(model_file)
    print(f"Loaded model: {ticker}")

    end_date = date.today() + timedelta(days=days)
    dates = pd.date_range(
        start="2020-01-01",
        end=end_date.strftime("%Y-%m-%d"),
    )
    df = pd.DataFrame({"ds": dates})

    forecast = model.predict(df)
    _prediction_list = forecast.tail(days).to_dict(orient="records")
    prediction_result = []
    for row in _prediction_list:
        prediction_result.append(
            {
                "ds": row["ds"].strftime("%Y-%m-%d"),
                "prediction": row["yhat"],
                "lower_bound": row["yhat_lower"],
                "upper_bound": row["yhat_upper"],
            }
        )

    return prediction_result


# -*- Pydantic models for prediction request and response
class PredictionRequest(BaseModel):
    ticker: str = DEFAULT_TICKER
    days: int = DEFAULT_DAYS_TO_PREDICT


class PredictionResponse(BaseModel):
    ticker: str
    days: int
    result: list


@prediction_router.post("/ticker", response_model=PredictionResponse)
def predict_stock_price(prediction_request: PredictionRequest):
    prediction_result = predict(
        ticker=prediction_request.ticker,
        days=prediction_request.days,
    )
    return PredictionResponse(
        ticker=prediction_request.ticker,
        days=prediction_request.days,
        result=prediction_result,
    )

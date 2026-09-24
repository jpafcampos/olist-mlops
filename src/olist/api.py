import os
from contextlib import asynccontextmanager

import pandas as pd
import mlflow
from fastapi import FastAPI
from pydantic import BaseModel

from olist.features import FEATURES

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
MODEL_URI = "models:/olist-delay@champion"


ml = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml["model"] = mlflow.pyfunc.load_model(MODEL_URI)
    yield
    ml.clear()


app = FastAPI(title="Olist MLOps API", lifespan=lifespan)


class PredictRequest(BaseModel):
    promised_days: int
    purchase_month: int
    purchase_dow: int
    purchase_hour: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    X = pd.DataFrame([[getattr(req, f) for f in FEATURES]], columns=FEATURES)
    pred = int(ml["model"].predict(X)[0])
    return {"prediction": pred, "label": "late" if pred == 1 else "on_time"}
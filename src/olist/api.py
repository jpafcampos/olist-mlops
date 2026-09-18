import os
from contextlib import asynccontextmanager

import numpy as np
import mlflow
from fastapi import FastAPI
from pydantic import BaseModel

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
MODEL_URI = "models:/olist-delay@champion"

# Guarda o modelo carregado; começa vazio.
ml = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Roda quando o SERVIDOR sobe (não no import). Carrega o modelo aqui.
    ml["model"] = mlflow.pyfunc.load_model(MODEL_URI)
    yield
    # (depois do yield rodaria limpeza no shutdown, se precisasse)
    ml.clear()


app = FastAPI(title="Olist MLOps API", lifespan=lifespan)


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    X = np.array([req.features])
    pred = int(ml["model"].predict(X)[0])
    return {"prediction": pred, "label": "late" if pred == 1 else "on_time"}
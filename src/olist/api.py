import os
import numpy as np
import mlflow
from fastapi import FastAPI
from pydantic import BaseModel

# Mesmo "endereço" do MLflow que o train.py usou. Via variável de ambiente
# para o Docker poder trocar depois; o default local aponta pro sqlite do projeto.
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))

MODEL_URI = "models:/olist-delay@champion"

app = FastAPI(title="Olist MLOps API")

# Carrega o modelo UMA vez, quando o servidor sobe — nunca a cada requisição.
model = mlflow.pyfunc.load_model(MODEL_URI)


class PredictRequest(BaseModel):
    features: list[float]  # 3 números (placeholder até o passo 2 trazer features reais)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    X = np.array([req.features])
    pred = int(model.predict(X)[0])
    return {"prediction": pred, "label": "late" if pred == 1 else "on_time"}
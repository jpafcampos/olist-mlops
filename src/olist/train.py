import mlflow
import mlflow.sklearn
import numpy as np
from mlflow.models import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Onde o MLflow guarda tudo. sqlite (um banco) é obrigatório p/ o registry;
# o file store simples (./mlruns) NÃO suporta registrar modelos.
import os
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
mlflow.set_experiment("olist-delay")

# Toy example
rng = np.random.default_rng(42)
X = rng.normal(size=(500, 3))
y = (X[:, 0] + rng.normal(size=500) > 0).astype(int)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

params = {"C": 1.0, "max_iter": 200}
model = LogisticRegression(**params)
model.fit(X_tr, y_tr)
acc = accuracy_score(y_te, model.predict(X_te))
print(f"accuracy = {acc:.3f}")

with mlflow.start_run(run_name="baseline-lr"):
    mlflow.log_params(params)
    mlflow.log_metric("accuracy", acc)
    signature = infer_signature(X_te, model.predict(X_te))
    info = mlflow.sklearn.log_model(
        sk_model=model,
        name="model",                       # MLflow 3 usa 'name'
        signature=signature,
        input_example=X_te[:5],
        registered_model_name="olist-delay",  # cria/versiona no registry
    )

print("model_uri:", info.model_uri)
import os
import duckdb
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, average_precision_score

from olist.features import FEATURES

mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
mlflow.set_experiment("olist-delay")

TARGET = "late"

# 1. Lê as features reais direto do DuckDB
con = duckdb.connect("olist.duckdb")
df = con.execute(f"SELECT {', '.join(FEATURES)}, {TARGET} FROM stg_orders").df()
con.close()

X, y = df[FEATURES], df[TARGET]
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y   # mantém os 8,1% nos dois lados
)

# 2. Baseline honesto: pesa a classe rara
params = {"C": 1.0, "max_iter": 1000, "class_weight": "balanced"}
model = LogisticRegression(**params)
model.fit(X_tr, y_tr)

# 3. Métricas certas para alvo desbalanceado, na classe 'late' (=1)
pred = model.predict(X_te)
proba = model.predict_proba(X_te)[:, 1]
metrics = {
    "precision_late": precision_score(y_te, pred, pos_label=1, zero_division=0),
    "recall_late": recall_score(y_te, pred, pos_label=1),
    "auc_pr": average_precision_score(y_te, proba),
    "base_rate": y.mean(),   # 0.081 — o piso de referência
}
for k, v in metrics.items():
    print(f"{k:16s} {v:.3f}")

# 4. Registra no MLflow
with mlflow.start_run(run_name="logreg-real-features"):
    mlflow.log_params(params)
    mlflow.log_param("features", FEATURES)
    mlflow.log_metrics(metrics)
    signature = infer_signature(X_te, pred)
    info = mlflow.sklearn.log_model(
        sk_model=model,
        name="model",
        signature=signature,
        input_example=X_te.iloc[:5],
        registered_model_name="olist-delay",
    )
print("model_uri:", info.model_uri)
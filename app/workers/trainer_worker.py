from __future__ import annotations

import time
import redis

import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from app.services.mlflow_service import mlflow_service
from app.core.config import settings


def train_and_register(registered_name: str = "demo_iris_model") -> str:
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    with mlflow_service.start_run() as run:
        params = {"n_estimators": 50, "random_state": 42}
        mlflow.log_params(params)

        clf = RandomForestClassifier(n_estimators=params["n_estimators"], random_state=params["random_state"])
        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)
        acc = float(accuracy_score(y_test, preds))
        mlflow.log_metric("accuracy", acc)

        # log model artifact
        mlflow.sklearn.log_model(clf, "model")
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"

        # try to register (may fail if registry not configured); always persist run mapping
        if registered_name:
            try:
                mlflow.register_model(model_uri, registered_name)
            except Exception:
                pass
            try:
                r.set(f"model_latest_run:{registered_name}", run_id)
            except Exception:
                pass

        print(f"Trained and logged model run_id={run_id}, accuracy={acc}")
        return run_id


if __name__ == "__main__":
    # train once initially, then retrain periodically
    while True:
        try:
            train_and_register()
        except Exception as exc:
            print("Trainer error:", exc)
        time.sleep(60 * 60)  # retrain hourly


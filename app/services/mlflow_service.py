from __future__ import annotations

import os
from typing import Any

import mlflow
import mlflow.sklearn
import mlflow.pyfunc

from app.core.config import settings


class MLflowService:
    def __init__(self) -> None:
        # ensure environment variables for S3/MinIO are set for mlflow boto
        os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = settings.mlflow_s3_endpoint_url
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    def start_run(self, **kwargs: Any):
        return mlflow.start_run(**kwargs)

    def log_params(self, params: dict[str, Any]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

    def log_model(self, model, artifact_path: str = "model", registered_name: str | None = None) -> tuple[str, str]:
        if registered_name:
            mlflow.sklearn.log_model(model, artifact_path, registered_model_name=registered_name)
        else:
            mlflow.sklearn.log_model(model, artifact_path)
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/{artifact_path}"
        return run_id, model_uri

    def load_model_by_run(self, run_id: str, artifact_path: str = "model"):
        return mlflow.pyfunc.load_model(f"runs:/{run_id}/{artifact_path}")

    def load_model_by_registry(self, model_name: str):
        try:
            return mlflow.pyfunc.load_model(f"models:/{model_name}/latest")
        except Exception:
            return mlflow.pyfunc.load_model(f"models:/{model_name}/1")


mlflow_service = MLflowService()

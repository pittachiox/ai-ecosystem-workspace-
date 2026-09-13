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
        os.environ.setdefault("AWS_ACCESS_KEY_ID", settings.aws_access_key_id)
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", settings.aws_secret_access_key)
        os.environ.setdefault("MLFLOW_S3_ENDPOINT_URL", settings.mlflow_s3_endpoint_url)
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    def start_run(self, **kwargs: Any):
        try:
            return mlflow.start_run(**kwargs)
        except Exception:
            # fallback: use local file-backed tracking (shared volume '/mlruns')
            local_uri = "file:///mlruns"
            os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
            mlflow.set_tracking_uri(local_uri)
            # ensure default experiment exists for file store
            try:
                mlflow.set_experiment("Default")
            except Exception:
                pass
            return mlflow.start_run(**kwargs)

    def log_params(self, params: dict[str, Any]) -> None:
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        for k, v in metrics.items():
            mlflow.log_metric(k, v)

    def log_model(self, model, artifact_path: str = "model", registered_name: str | None = None) -> tuple[str, str]:
        mlflow.sklearn.log_model(model, artifact_path)
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/{artifact_path}"
        if registered_name:
            try:
                mlflow.register_model(model_uri, registered_name)
            except Exception:
                pass
        return run_id, model_uri

    def load_model_by_run(self, run_id: str, artifact_path: str = "model"):
        return mlflow.pyfunc.load_model(f"runs:/{run_id}/{artifact_path}")

    def load_model_by_registry(self, model_name: str):
        return mlflow.pyfunc.load_model(f"models:/{model_name}/latest")


mlflow_service = MLflowService()

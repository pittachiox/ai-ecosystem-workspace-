from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Ecosystem API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    arq_redis_queue_name: str = Field(default="ai-ecosystem", alias="ARQ_REDIS_QUEUE_NAME")

    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")
    minio_default_bucket: str = Field(default="datasets", alias="MINIO_DEFAULT_BUCKET")

    label_studio_url: str = Field(default="http://localhost:8080", alias="LABEL_STUDIO_URL")
    label_studio_api_key: str = Field(default="", alias="LABEL_STUDIO_API_KEY")

    # MLflow / model registry settings
    mlflow_tracking_uri: str = Field(default="http://localhost:5000", alias="MLFLOW_TRACKING_URI")
    mlflow_s3_endpoint_url: str = Field(default="http://localhost:9000", alias="MLFLOW_S3_ENDPOINT_URL")
    aws_access_key_id: str = Field(default="minioadmin", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="minioadmin", alias="AWS_SECRET_ACCESS_KEY")
    mlflow_artifact_root: str = Field(default="s3://mlflow/", alias="MLFLOW_ARTIFACT_ROOT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

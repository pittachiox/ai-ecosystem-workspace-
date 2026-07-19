from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6380"
    arq_redis_queue_name: str = "default"
    database_url: str = "postgresql://labelstudio:labelstudio_pass@localhost:5432/labelstudio_db"
    label_studio_url: str = "http://localhost:8080"
    label_studio_api_key: Optional[str] = None

    class Config:
        env_file = Path(".env")
        env_file_encoding = "utf-8"


settings = Settings()

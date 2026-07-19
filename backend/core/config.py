from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6380
    postgres_user: str = "labelstudio"
    postgres_password: str = "labelstudio_pass"
    postgres_db: str = "labelstudio_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    label_studio_url: str = "http://localhost:8080"
    label_studio_api_key: Optional[str] = None
    arq_redis_queue_name: str = "default"

    class Config:
        env_file = Path(".env")
        env_file_encoding = "utf-8"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

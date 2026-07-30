from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI & AI Ecosystem Skeleton API"
    version: str = "1.0.0"

    class Config:
        env_file = ".env"

settings = Settings()

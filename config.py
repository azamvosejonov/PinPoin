from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://pinpoint:pinpoint123@postgres:5432/pinpoint"
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"


settings = Settings()

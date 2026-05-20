from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    GROQ_API_KEY: str
    BASE_URL: str = "http://localhost:8000"
    # Kvartira kodi shifrlash uchun (32 bayt hex)
    ENCRYPTION_KEY: str = "0" * 64
    # Rate limit
    RATE_LIMIT_PER_MINUTE: int = 60
    # Restoran ish vaqti default (HH:MM)
    DEFAULT_OPEN_TIME: str = "09:00"
    DEFAULT_CLOSE_TIME: str = "23:00"

    class Config:
        env_file = ".env"

settings = Settings()

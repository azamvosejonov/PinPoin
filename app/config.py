from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./pinpoint.db"
    openstreetmap_base_url: str = "https://nominatim.openstreetmap.org"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()

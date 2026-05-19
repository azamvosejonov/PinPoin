from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./pinpoint.db"
    openstreetmap_base_url: str = "https://nominatim.openstreetmap.org"
    cors_origins: list[str] = ["*"]
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    verification_token_expire_minutes: int = 60 * 24
    password_reset_token_expire_minutes: int = 15
    
    # Email settings (for password reset and verification)
    email_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "PinPoInt"
    
    # Telegram bot settings (alternative to email)
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()

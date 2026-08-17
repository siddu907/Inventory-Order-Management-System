from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:siddu@localhost:5432/inventory_management"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 2
    upload_dir: str = "app/uploads"
    max_upload_size: int = 5 * 1024 * 1024  

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_from_email: str = "noreply@example.com"
    smtp_from_name: str = "Inventory & Order Management"

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_enabled: bool = True
    cache_ttl: int = 5

    class Config:
        env_file = ".env"


settings = Settings()

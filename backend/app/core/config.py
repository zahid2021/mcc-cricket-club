from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MCC Cricket Club API"
    club_name: str = "Mustafa Cricket Club"
    club_short: str = "MCC"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./mcc.db"
    # Production: postgresql+psycopg://user:pass@host:5432/mcc

    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_use_long_random_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mcc-cricket-club.onrender.com",
    ]

    rate_limit_login_attempts: int = 5
    rate_limit_login_window_seconds: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False

    def sqlalchemy_url(self) -> str:
        url = self.database_url
        # Render provides postgresql:// — SQLAlchemy + psycopg3 needs this scheme
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and "+psycopg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

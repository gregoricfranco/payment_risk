from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Payment Risk AI"
    app_env: str = "development"
    log_level: str = "INFO"

    postgres_user: str = "payment_risk"
    postgres_password: str = "payment_risk"
    postgres_db: str = "payment_risk"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")

    redis_url: str = "redis://redis:6379/0"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

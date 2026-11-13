from app.core.config import Settings


def test_default_database_configuration() -> None:
    settings = Settings(_env_file=None)

    assert settings.sqlalchemy_database_url.startswith("postgresql+psycopg://")
    assert settings.redis_url.startswith("redis://")

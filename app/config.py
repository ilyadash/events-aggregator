from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_USER: str = "postgres_user"
    POSTGRES_PASSWORD: str = "postgres_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "aggregator_db"
    EVENT_PROVIDER_URL: str = "http://events-provider.dev-2.python-labs.ru"
    LMS_API_KEY: str = ""
    SYNC_CRON: str = "0 3 * * *"
    PAGE_SIZE: int = 20
    SEATS_CACHE_TTL: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,          # 1. Явный вызов в коде: Settings(app_name="...")
            settings_cls,           # 2. Дефолтные значения из кода
            env_settings,           # 3. Переменные окружения ОС
            dotenv_settings,        # 4. НАИВЫСШИЙ: Значения из .env файла
        )

    @property
    def DATABASE_URL(self) -> str:
        """Assemble the asyncpg DSN from individual PostgreSQL settings."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()

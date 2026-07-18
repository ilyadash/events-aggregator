from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_CONNECTION_STRING: str = ""
    POSTGRES_USERNAME: str = "postgres_user"
    POSTGRES_PASSWORD: str = "postgres_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE_NAME: str = "aggregator_db"
    EVENT_PROVIDER_URL: str = "http://student-system-events-provider-web.student-system-events-provider.svc:8000"
    LMS_API_KEY: str = ""
    SYNC_CRON: str = "0 3 * * *"
    PAGE_SIZE: int = 20
    SEATS_CACHE_TTL: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Assemble the asyncpg DSN from individual PostgreSQL settings."""
        url = self.POSTGRES_CONNECTION_STRING
        if url is None or url == '':
            url = f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@"
            url += f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            url += f"{self.POSTGRES_DATABASE_NAME}"
        elif not url.startswith("postgresql"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()

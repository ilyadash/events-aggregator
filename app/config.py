from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://aggregator:aggregator@localhost:5432/aggregator"
    provider_base_url: str = "http://events-provider.dev-2.python-labs.ru"
    provider_api_key: str = ""
    sync_cron: str = "0 3 * * *"
    page_size: int = 20
    seats_cache_ttl: int = 30


settings = Settings()
